import os
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from core.config import settings

from services.sql_agent.agent_tools import retrieve_schema, execute_sql, AgentContext
from services.sql_agent.agent_prompts import SQL_GENERATOR_PROMPT

class AnalyticsResponse(TypedDict):
    componentType: str  # 'GRAPH', 'TABLE', 'TEXT'
    title: str
    description: str
    config: dict
    data: list

class SQLAgentWorkflow:
    def __init__(self, model_family: str = "gemini", model_name: str = "gemini-3.8-flash"):
        
        family = model_family.lower() if model_family else "gemini"
        name = model_name if model_name else "gemini-3.8-flash"
        
        # Auto-remap deprecated/sunset Gemini models to the latest supported active model
        if family == "gemini" and ("2.0" in name or "2.5" in name):
            name = "gemini-3.8-flash"

        self.family = family
        self.model_name = name
        
        if family in ["groq", "llama", "openai"]:
            from langchain_groq import ChatGroq
            self.llm = ChatGroq(
                model=name,
                api_key=settings.GROQ_API_KEY,
                temperature=0.2,
                max_tokens=2048
            )
        else:
            self.llm = ChatGoogleGenerativeAI(
                model=name,
                google_api_key=settings.GEMINI_API_KEY,
                temperature=0.2, # Low temperature for accurate SQL generation
                max_retries=1    # Fail fast on rate-limits instead of hanging for 40+ seconds in retry sleep
            )
        
        # We bind the tools to the LLM
        self.tools = [execute_sql]

    async def run(
        self, 
        question: str, 
        vendor_id: str, 
        module_id: str, 
        history: str = "",
        module_system_prompt: str = "",
        business_context: str = "",
        user_context: dict = None
    ) -> dict:
        """
        Executes the LangGraph ReAct agent loop.
        """
        # Inject context for the tools to use and reset query cache
        AgentContext.vendor_id = vendor_id
        AgentContext.module_id = module_id
        AgentContext.last_sql_results = None
        AgentContext.last_sql_query = None
        
        # 1. Fetch schemas synchronously from Supabase BEFORE calling the LLM
        # This saves an entire LLM tool-calling loop (huge token savings)
        from services.sql_agent.agent_tools import retrieve_schema
        schemas_text = retrieve_schema.invoke({"query": question})
        
        # 2. Build caller context and RLS scoping
        caller_context_lines = []
        if user_context and isinstance(user_context, dict):
            role = user_context.get("role", "USER")
            caller_context_lines.append(f"- Caller Role: {role}")
            for key, val in user_context.items():
                if key != "role" and val:
                    caller_context_lines.append(f"- Mandatory Scope: Tables containing `{key}` MUST be filtered by `{key} = '{val}'`")
            caller_context_text = "\n".join(caller_context_lines)
        else:
            caller_context_text = f"- Caller Role: TENANT_ADMIN\n- Mandatory Scope: Tables containing `company_id` MUST be filtered by `company_id = '{vendor_id}'`. Tables containing `vendor_id` MUST be filtered by `vendor_id = '{vendor_id}'`."

        # 3. Inject the vendor_id, history, schemas, caller_context, and dynamic prompts
        dynamic_prompt = SQL_GENERATOR_PROMPT.replace(
            "{caller_context}", caller_context_text
        ).replace(
            "{vendor_id}", vendor_id
        ).replace(
            "{schemas}", schemas_text
        ).replace(
            "{history}", history
        ).replace(
            "{module_system_prompt}", module_system_prompt or "No specific module instructions provided."
        ).replace(
            "{business_context}", business_context or "No specific business context found for this query."
        )
        
        # 4. We create the ReAct agent graph here so we can use the dynamic prompt
        agent = create_react_agent(
            self.llm,
            self.tools,
            prompt=dynamic_prompt
        )
        
        inputs = {"messages": [HumanMessage(content=question)]}
        
        # Execute the agent graph
        # This will loop internally: Think -> Execute SQL -> Output
        from langgraph.errors import GraphRecursionError
        from loguru import logger
        import json
        
        try:
            final_state = await agent.ainvoke(
                inputs, 
                config={"recursion_limit": 6}
            )
        except Exception as e:
            # RESILIENT FALLBACK: If SQL query already succeeded and fetched data,
            # but the LLM final formatting call failed (e.g. rate limit, quota 429),
            # return the SQL results directly as a TABLE component!
            if AgentContext.last_sql_results is not None:
                logger.warning(
                    f"LLM final response generation failed ({type(e).__name__}: {e}), "
                    f"but SQL executed successfully with {len(AgentContext.last_sql_results)} rows. "
                    f"Serving data directly via fallback TABLE component."
                )
                cols = list(AgentContext.last_sql_results[0].keys()) if AgentContext.last_sql_results else []
                fallback_structured = {
                    "components": [
                        {
                            "componentType": "TABLE",
                            "title": "Query Results",
                            "description": f"Retrieved {len(AgentContext.last_sql_results)} record(s) matching your request.",
                            "config": {"columns": cols},
                            "data": AgentContext.last_sql_results
                        }
                    ],
                    "suggestions": [
                        "Would you like to filter these results further?",
                        "Do you need a summary of these records?"
                    ]
                }
                return {
                    "raw_response": json.dumps(fallback_structured, default=str),
                    "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                }
                
            if isinstance(e, GraphRecursionError):
                logger.warning(f"SQLAgentWorkflow hit recursion limit: {e}")
                return {
                    "raw_response": "I am sorry, but I was unable to construct a valid SQL query to answer your question after several attempts. Please try rephrasing your request."
                }

            raise e
        
        # The final message from the LLM should be the raw response
        final_message = final_state["messages"][-1].content
        
        # Extract and aggregate token usage across all steps in the ReAct loop
        total_prompt_tokens = 0
        total_completion_tokens = 0
        
        for msg in final_state["messages"]:
            # Newer LangChain versions use usage_metadata
            if hasattr(msg, "usage_metadata") and msg.usage_metadata:
                usage = msg.usage_metadata
                total_prompt_tokens += usage.get("input_tokens", 0)
                total_completion_tokens += usage.get("output_tokens", 0)
            # Fallback for older integrations
            elif hasattr(msg, "response_metadata") and "token_usage" in msg.response_metadata:
                usage = msg.response_metadata["token_usage"]
                total_prompt_tokens += usage.get("prompt_tokens", 0)
                total_completion_tokens += usage.get("completion_tokens", 0)
        
        return {
            "raw_response": final_message,
            "usage": {
                "prompt_tokens": total_prompt_tokens,
                "completion_tokens": total_completion_tokens,
                "total_tokens": total_prompt_tokens + total_completion_tokens
            }
        }

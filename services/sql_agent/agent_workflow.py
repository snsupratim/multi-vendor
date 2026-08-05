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
    def __init__(self, model_family: str = "gemini", model_name: str = "gemini-2.5-flash"):
        
        family = model_family.lower() if model_family else "gemini"
        name = model_name if model_name else "gemini-2.5-flash"
        
        if family == "groq" or family == "llama":
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
                temperature=0.2 # Low temperature for accurate SQL generation
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
        business_context: str = ""
    ) -> dict:
        """
        Executes the LangGraph ReAct agent loop.
        """
        # Inject context for the tools to use
        AgentContext.vendor_id = vendor_id
        AgentContext.module_id = module_id
        
        # 1. Fetch schemas synchronously from Supabase BEFORE calling the LLM
        # This saves an entire LLM tool-calling loop (huge token savings)
        from services.sql_agent.agent_tools import retrieve_schema
        schemas_text = retrieve_schema.invoke({"query": question})
        
        # 2. Inject the vendor_id, history, schemas, and dynamic prompts
        dynamic_prompt = SQL_GENERATOR_PROMPT.replace(
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
        
        # 3. We create the ReAct agent graph here so we can use the dynamic prompt
        agent = create_react_agent(
            self.llm,
            self.tools,
            prompt=dynamic_prompt
        )
        
        inputs = {"messages": [HumanMessage(content=question)]}
        
        # Execute the agent graph
        # This will loop internally: Think -> Retrieve Schema -> Think -> Execute SQL -> Output
        from langgraph.errors import GraphRecursionError
        
        try:
            final_state = await agent.ainvoke(
                inputs, 
                config={"recursion_limit": 5}
            )
        except GraphRecursionError:
            return {
                "raw_response": "I am sorry, but I was unable to construct a valid SQL query to answer your question after several attempts. Please try rephrasing your request."
            }
        
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

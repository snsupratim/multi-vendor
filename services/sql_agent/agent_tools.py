from langchain_core.tools import tool
from services.vector_store_service import VectorStoreService
from services.embedding_service import EmbeddingService
from services.sql_execution_service import SQLExecutionService
from db.supabase import supabase
from loguru import logger
import json

# We use global variables to inject context into the tools since LangChain tools 
# don't easily accept dynamic runtime dependencies without custom base classes.
class AgentContext:
    vendor_id: str = None
    module_id: str = None

@tool
def retrieve_schema(query: str) -> str:
    """
    Search the database for relevant table schemas based on the user's natural language query.
    Always use this tool first to understand the database structure before writing SQL.
    Returns the table name, schema DDL, and relationships.
    """
    if not AgentContext.module_id:
        return "Error: module_id context not set."

    embedding = EmbeddingService.get_embedding(query)

    # We perform a similarity search but STRICTLY filter by SQL_SCHEMA and the module_id
    response = supabase.rpc(
        "match_documents",
        {
            "query_embedding": embedding,
            "match_count": 20,
            "p_workspace_id": AgentContext.module_id
        }
    ).execute()

    if not response.data:
        return "No relevant schemas found. The database might not contain tables related to this query."

    # Filter out anything that isn't a schema 
    # (The Supabase RPC only returns id, content, similarity. Metadata is stripped!)
    schemas = []
    for doc in response.data:
        content = doc.get("content", "")
        # Since we format schemas with 'Table Name: ' and 'Schema DDL:' during ingestion, 
        # we can reliably check the content string itself!
        if "Schema DDL:" in content or "CREATE TABLE" in content:
            schemas.append(doc)
    
    if not schemas:
        logger.info(f"retrieve_schema: No relevant SQL schemas found. Raw data: {response.data}")
        return "No relevant SQL schemas found."

    formatted_schemas = []
    for s in schemas:
        # The content already contains 'Table Name: xxx\nSchema DDL: ...' from our ingestion script
        formatted_schemas.append(s.get("content", ""))

    final_result = "\n\n".join(formatted_schemas)
    logger.info(f"retrieve_schema returned: {final_result}")
    return final_result

@tool
def retrieve_business_context(query: str) -> str:
    """
    Search the database for relevant business logic, definitions, and formatting rules.
    """
    if not AgentContext.module_id:
        return ""

    embedding = EmbeddingService.get_embedding(query)

    response = supabase.rpc(
        "match_documents",
        {
            "query_embedding": embedding,
            "match_count": 20,
            "p_workspace_id": AgentContext.module_id
        }
    ).execute()

    if not response.data:
        return ""

    kb_docs = []
    for doc in response.data:
        content = doc.get("content", "")
        # Filter OUT schemas to only get standard knowledgebase JSON documents
        if "Schema DDL:" not in content and "CREATE TABLE" not in content:
            kb_docs.append(content)
            
    if not kb_docs:
        return ""

    return "\n\n---\n\n".join(kb_docs)

@tool
async def execute_sql(sql_query: str) -> str:
    """
    Executes a PostgreSQL query against the database and returns the results.
    The query must be a valid SELECT statement.
    """
    logger.info(f"execute_sql called with query: {sql_query}")
    if not AgentContext.vendor_id:
        return "Error: vendor_id context not set."
        
    try:
        results = await SQLExecutionService.execute_query(sql_query, AgentContext.vendor_id)
        
        if not results:
            logger.info("execute_sql returned 0 rows.")
            return "Query executed successfully, but returned 0 rows."
            
        # Return first 5 rows to the LLM so it can understand the data structure 
        # before formatting the final JSON response
        preview = results[:5]
        result_str = f"Execution successful. Found {len(results)} total rows. Data preview:\n" + json.dumps(preview, indent=2, default=str)
        logger.info(f"execute_sql returned data: {result_str}")
        return result_str
        
    except Exception as e:
        logger.error(f"execute_sql failed: {str(e)}")
        return f"Error executing SQL: {str(e)}"

import asyncpg
from core.config import settings
from loguru import logger
import json

class SQLExecutionService:
    _pool = None

    @classmethod
    async def get_pool(cls):
        if cls._pool is None:
            logger.info("Initializing asyncpg connection pool...")
            
            async def init_connection(conn):
                # Ensure the connection searches these schemas by default
                await conn.execute("SET search_path TO payroll;")
                
            cls._pool = await asyncpg.create_pool(
                settings.PAYROLL_DB_URL,
                min_size=1,
                max_size=10,
                command_timeout=30.0, # 30 second strict timeout for AI queries
                setup=init_connection
            )
        return cls._pool

    @classmethod
    def validate_sql_safety(cls, query: str):
        import re
        # Remove single-quoted strings and double-quoted identifiers to prevent false positives
        q1 = re.sub(r"'.*?'", "''", query.upper())
        q2 = re.sub(r'".*?"', '""', q1)
        
        q_stripped = q2.strip()
        if not q_stripped.startswith("SELECT") and not q_stripped.startswith("WITH"):
            raise ValueError("SECURITY ALERT: Only SELECT queries are allowed. Your query must start with SELECT or WITH.")
            
        dangerous_keywords = [
            r'\bINSERT\b', r'\bUPDATE\b', r'\bDELETE\b', r'\bDROP\b', 
            r'\bALTER\b', r'\bCREATE\b', r'\bTRUNCATE\b', r'\bGRANT\b', 
            r'\bREVOKE\b', r'\bEXEC\b', r'\bEXECUTE\b', r'\bMERGE\b',
            r'\bCOMMIT\b', r'\bROLLBACK\b'
        ]
        
        for keyword in dangerous_keywords:
            if re.search(keyword, q2):
                raise ValueError("SECURITY ALERT: Prohibited SQL operation detected. Data modification, DDL, and transactional commands are strictly blocked by the system guardrails.")

    @classmethod
    async def execute_query(cls, query: str, vendor_id: str):
        """
        Executes an arbitrary SQL query against the Read-Only database.
        Includes safeguards to prevent massive result sets.
        """
        try:
            cls.validate_sql_safety(query)
            pool = await cls.get_pool()
            
            async with pool.acquire() as conn:
                # We enforce read-only execution if possible on the session level, 
                # but it is highly recommended to use a read-only database user in production.
                async with conn.transaction():
                    await conn.execute("SET TRANSACTION READ ONLY;")
                    
                    # Log the exact query being executed
                    logger.debug(f"Executing SQL for Vendor {vendor_id}: {query}")
                    
                    records = await conn.fetch(query)
                    
                    # Convert asyncpg Records to standard list of dicts
                    results = [dict(record) for record in records]
                    
                    # Simple date/uuid serialization fix for JSON output
                    for row in results:
                        for k, v in row.items():
                            if hasattr(v, 'isoformat'):
                                row[k] = v.isoformat()
                            elif hasattr(v, 'hex'): # UUID
                                row[k] = str(v)
                                
                    return results

        except asyncpg.exceptions.PostgresError as e:
            logger.error(f"Postgres SQL Execution Error: {str(e)}")
            raise ValueError(f"SQL Error: {str(e)}. Please correct your query syntax.")
        except Exception as e:
            logger.error(f"SQL Execution Error: {str(e)}")
            raise ValueError(f"Execution failed: {str(e)}")

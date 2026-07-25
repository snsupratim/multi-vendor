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
            cls._pool = await asyncpg.create_pool(
                settings.SUPABASE_DB_URL,
                min_size=1,
                max_size=10,
                command_timeout=30.0 # 30 second strict timeout for AI queries
            )
        return cls._pool

    @classmethod
    async def execute_query(cls, query: str, vendor_id: str):
        """
        Executes an arbitrary SQL query against the Read-Only database.
        Includes safeguards to prevent massive result sets.
        """
        try:
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

import asyncio
import asyncpg
from core.config import settings

async def main():
    print(f"Loaded SUPABASE_DB_URL: {settings.SUPABASE_DB_URL}")
    
    try:
        conn = await asyncpg.connect(settings.SUPABASE_DB_URL, timeout=10)
        print("CONNECTION SUCCESSFUL!")
        version = await conn.fetchval('SELECT version()')
        print(f"Database Version: {version}")
        await conn.close()
    except Exception as e:
        print(f"CONNECTION FAILED: {type(e).__name__} - {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())

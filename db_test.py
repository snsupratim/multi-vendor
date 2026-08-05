import asyncio
import asyncpg
from core.config import settings

async def main():
    try:
        print(f"Loaded PAYROLL_DB_URL: {settings.PAYROLL_DB_URL}")
        
        # Connect to the database
        conn = await asyncpg.connect(settings.PAYROLL_DB_URL, timeout=10)
        print("Successfully connected to the PostgreSQL database!")
        version = await conn.fetchval('SELECT version()')
        print(f"Database Version: {version}")
        await conn.close()
    except Exception as e:
        print(f"CONNECTION FAILED: {type(e).__name__} - {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())

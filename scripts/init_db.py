"""
Database initialization script.
Creates all tables and optionally seeds initial data.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.db import engine, Base, async_session_maker
from backend.app.models.user import User
from backend.app.models.image_job import ImageJob
from backend.app.models.payment import Payment


async def init_database():
    """Initialize database tables."""
    print("🔧 Initializing database...")
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database initialized successfully!")
    print("\n📊 Created tables:")
    for table in Base.metadata.tables:
        print(f"  - {table}")


async def drop_database():
    """Drop all database tables."""
    print("⚠️ Dropping all tables...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    print("✅ All tables dropped!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database management script")
    parser.add_argument(
        "--drop", 
        action="store_true", 
        help="Drop all tables before creating"
    )
    
    args = parser.parse_args()
    
    async def main():
        if args.drop:
            await drop_database()
        await init_database()
    
    asyncio.run(main())

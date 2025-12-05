"""
Seed test data script.
Creates sample users and image jobs for testing.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.db import async_session_maker
from backend.app.models.user import User
from backend.app.models.image_job import ImageJob, ImageStyle, JobStatus
from backend.app.services.auth import hash_password


async def seed_data():
    """Seed the database with test data."""
    print("🌱 Seeding database with test data...")
    
    async with async_session_maker() as session:
        # Create test users
        test_users = [
            {
                "email": "demo@toonify.app",
                "password": "demo12345",
                "full_name": "Demo User",
                "is_admin": False
            },
            {
                "email": "admin@toonify.app",
                "password": "admin12345",
                "full_name": "Admin User",
                "is_admin": True
            }
        ]
        
        created_users = []
        for user_data in test_users:
            user = User(
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                full_name=user_data["full_name"],
                is_admin=user_data["is_admin"]
            )
            session.add(user)
            created_users.append(user_data)
        
        await session.commit()
        
        print("\n✅ Created test users:")
        for user in created_users:
            print(f"  📧 {user['email']} / {user['password']}")
        
        print("\n🎉 Seeding complete!")
        print("\nYou can now login with:")
        print("  Email: demo@toonify.app")
        print("  Password: demo12345")


if __name__ == "__main__":
    asyncio.run(seed_data())

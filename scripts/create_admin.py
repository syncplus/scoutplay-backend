import asyncio
from app.database import AsyncSessionLocal
from app.services.user import UserService
from app.models.user import UserRole

async def main():
    async with AsyncSessionLocal() as session:
        svc = UserService(session)
        user = await svc.create(
            name     = "Admin",
            username = "admin",
            email    = "admin@scoutplay.com",
            password = "Admin@123",
            role     = UserRole.ADMIN,
        )
        print(f"Admin criado: {user.id}")

asyncio.run(main())
import asyncio
import sys

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.user import User
from app.services.utils.security import hash_password

#python -m scripts.reset_password <username_or_email> <nova_senha>
async def main(identifier: str, new_password: str):
    async with AsyncSessionLocal() as session:
        ident = identifier.lower()
        result = await session.execute(
            select(User).where(
                (User.email == ident) | (User.username == ident)
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            print(f"Usuário não encontrado: {identifier}")
            sys.exit(1)

        username, email = user.username, user.email
        user.password = hash_password(new_password)
        await session.commit()
        print(f"Senha redefinida para {username} ({email})")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python -m scripts.reset_password <email_ou_username> <nova_senha>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2]))

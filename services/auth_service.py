from repositories.user_repository import UserRepository
from core.security import (
    hash_password,
    verify_password,
    create_access_token
)


class AuthService:

    @staticmethod
    async def register(payload):

        existing = await UserRepository.find_by_email(
            payload.email
        )

        if existing:
            raise Exception("User already exists")

        user = {
            "name": payload.name,
            "email": payload.email,
            "password": hash_password(payload.password),
            "role": "SUPER_ADMIN"
        }

        user_id = await UserRepository.create_user(user)

        return {
            "user_id": user_id
        }

    @staticmethod
    async def login(payload):

        user = await UserRepository.find_by_email(
            payload.email
        )

        if not user:
            raise Exception("Invalid credentials")

        valid = verify_password(
            payload.password,
            user["password"]
        )

        if not valid:
            raise Exception("Invalid credentials")

        token = create_access_token(
            {
                "sub": user["email"],
                "role": user["role"]
            }
        )

        return {
            "access_token": token,
            "token_type": "bearer"
        }
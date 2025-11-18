"""User models and OAuth authentication setup."""

import logging
from typing import Optional

from bson import ObjectId
from fastapi import Depends, Request
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import BearerTransport, JWTStrategy, AuthenticationBackend
from fastapi_users.manager import BaseUserManager
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.clients.github import GitHubOAuth2
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import Field, ConfigDict

from api.config import settings
from api.database.async_mongodb import async_mongodb_adapter
from api.auth.database import MongoDBUserDatabase

logger = logging.getLogger(__name__)


class User:
    """User model implementing UserProtocol for FastAPI-Users v15."""

    def __init__(
        self,
        id: ObjectId,
        email: str,
        hashed_password: str = "",
        is_active: bool = True,
        is_superuser: bool = False,
        is_verified: bool = False,
        organization_id: Optional[ObjectId] = None,
        plan: str = "free",
        oauth_accounts: Optional[list[dict]] = None,
    ):
        """Initialize user."""
        self.id = id
        self.email = email
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.is_superuser = is_superuser
        self.is_verified = is_verified
        self.organization_id = organization_id
        self.plan = plan
        self.oauth_accounts = oauth_accounts or []

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create user from dictionary."""
        return cls(
            id=data.get("_id", data.get("id")),
            email=data["email"],
            hashed_password=data.get("hashed_password", ""),
            is_active=data.get("is_active", True),
            is_superuser=data.get("is_superuser", False),
            is_verified=data.get("is_verified", False),
            organization_id=data.get("organization_id"),
            plan=data.get("plan", "free"),
            oauth_accounts=data.get("oauth_accounts", []),
        )

    def to_dict(self) -> dict:
        """Convert user to dictionary."""
        result = {
            "_id": self.id,
            "email": self.email,
            "hashed_password": self.hashed_password,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "is_verified": self.is_verified,
        }
        if self.organization_id:
            result["organization_id"] = self.organization_id
        if self.plan:
            result["plan"] = self.plan
        if self.oauth_accounts:
            result["oauth_accounts"] = self.oauth_accounts
        return result


class UserManager(BaseUserManager[User, ObjectId]):
    """Custom user manager."""

    def __init__(self, user_db: MongoDBUserDatabase):
        """Initialize user manager.

        Args:
            user_db: MongoDB user database
        """
        from fastapi_users.password import PasswordHelper

        super().__init__(user_db, PasswordHelper())

    async def on_after_register(self, user: User, request: Request | None = None) -> None:
        """Called after user registration."""
        logger.info("User %s has registered", user.id)

    async def on_after_update(
        self,
        user: User,
        update_dict: dict,
        request: Request | None = None,
    ) -> None:
        """Called after user update."""
        logger.info("User %s has been updated", user.id)


async def get_user_db() -> MongoDBUserDatabase:
    """Get MongoDB user database adapter.

    Yields:
        MongoDBUserDatabase instance
    """
    await async_mongodb_adapter.connect()
    db: AsyncIOMotorDatabase = async_mongodb_adapter.get_database()
    collection = db.users
    yield MongoDBUserDatabase(collection)


async def get_user_manager(user_db: MongoDBUserDatabase = Depends(get_user_db)) -> UserManager:
    """Get user manager instance.

    Args:
        user_db: MongoDB user database

    Yields:
        UserManager instance
    """
    yield UserManager(user_db)


def get_jwt_authentication() -> AuthenticationBackend:
    """Get JWT authentication backend.

    Returns:
        AuthenticationBackend instance
    """
    bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
    jwt_strategy = JWTStrategy(
        secret=settings.secret_key,
        lifetime_seconds=settings.access_token_expire_minutes * 60,
    )
    return AuthenticationBackend(
        name="jwt",
        transport=bearer_transport,
        get_strategy=lambda: jwt_strategy,
    )


jwt_authentication = get_jwt_authentication()


def get_google_oauth_client() -> GoogleOAuth2:
    """Get Google OAuth client.

    Returns:
        GoogleOAuth2 instance
    """
    return GoogleOAuth2(
        client_id=settings.google_oauth_client_id,
        client_secret=settings.google_oauth_client_secret,
    )


def get_github_oauth_client() -> GitHubOAuth2:
    """Get GitHub OAuth client.

    Returns:
        GitHubOAuth2 instance
    """
    return GitHubOAuth2(
        client_id=settings.github_oauth_client_id,
        client_secret=settings.github_oauth_client_secret,
    )


google_oauth_client = get_google_oauth_client()
github_oauth_client = get_github_oauth_client()


fastapi_users = FastAPIUsers[User, ObjectId](
    get_user_manager,
    [jwt_authentication],
)

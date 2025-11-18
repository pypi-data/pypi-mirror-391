"""MongoDB database adapter for FastAPI-Users."""

import logging
from typing import Optional, TYPE_CHECKING

from bson import ObjectId
from fastapi_users.db.base import BaseUserDatabase
from motor.motor_asyncio import AsyncIOMotorCollection

if TYPE_CHECKING:
    from api.auth.users import User

logger = logging.getLogger(__name__)


class MongoDBUserDatabase(BaseUserDatabase["User", ObjectId]):
    """MongoDB user database adapter for FastAPI-Users."""

    def __init__(self, collection: AsyncIOMotorCollection):
        """Initialize MongoDB user database.

        Args:
            collection: Motor collection instance
        """
        self.collection = collection

    async def get(self, id: ObjectId) -> Optional["User"]:
        """Get user by ID.

        Args:
            id: User ID

        Returns:
            User instance or None
        """
        from api.auth.users import User

        user_dict = await self.collection.find_one({"_id": id})
        if user_dict:
            return User.from_dict(user_dict)
        return None

    async def get_by_email(self, email: str) -> Optional["User"]:
        """Get user by email.

        Args:
            email: User email

        Returns:
            User instance or None
        """
        from api.auth.users import User

        user_dict = await self.collection.find_one({"email": email})
        if user_dict:
            return User.from_dict(user_dict)
        return None

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> Optional["User"]:
        """Get user by OAuth account.

        Args:
            oauth: OAuth provider name
            account_id: OAuth account ID

        Returns:
            User instance or None
        """
        from api.auth.users import User

        user_dict = await self.collection.find_one(
            {"oauth_accounts": {"$elemMatch": {"oauth_name": oauth, "account_id": account_id}}}
        )
        if user_dict:
            return User.from_dict(user_dict)
        return None

    async def create(self, user: "User") -> "User":
        """Create new user.

        Args:
            user: User instance

        Returns:
            Created User instance
        """
        user_dict = user.to_dict()
        await self.collection.insert_one(user_dict)
        return user

    async def update(self, user: "User") -> "User":
        """Update user.

        Args:
            user: User instance

        Returns:
            Updated User instance
        """
        user_dict = user.to_dict()
        user_id = user_dict.pop("_id")
        await self.collection.update_one({"_id": user_id}, {"$set": user_dict})
        return user

    async def delete(self, user: "User") -> None:
        """Delete user.

        Args:
            user: User instance
        """
        await self.collection.delete_one({"_id": user.id})


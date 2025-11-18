"""API key management and verification."""

import hashlib
import logging
import secrets
from datetime import datetime, timedelta
from typing import Any, Optional

from bson import ObjectId
from fastapi import HTTPException, status

from api.database.mongodb import mongodb_manager

logger = logging.getLogger(__name__)


class APIKeyManager:
    """Production-ready API key management."""

    @staticmethod
    def generate_api_key(prefix: str = "wistx") -> tuple[str, str]:
        """Generate secure API key.

        Args:
            prefix: Key prefix (default: "wistx")

        Returns:
            Tuple of (full_key, key_hash)
        """
        random_bytes = secrets.token_bytes(32)
        key = f"{prefix}_{random_bytes.hex()}"
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return key, key_hash

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash API key for storage.

        Args:
            api_key: API key string

        Returns:
            SHA-256 hash of the key
        """
        return hashlib.sha256(api_key.encode()).hexdigest()

    async def create_api_key(
        self,
        user_id: str,
        name: str,
        description: Optional[str] = None,
        organization_id: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> dict[str, Any]:
        """Create new API key for user.

        Args:
            user_id: User ID
            name: Key name
            description: Key description
            organization_id: Organization ID (optional)
            expires_at: Expiration date (optional)

        Returns:
            Dictionary with api_key, api_key_id, and metadata
        """
        db = mongodb_manager.get_database()
        collection = db.api_keys

        api_key, key_hash = self.generate_api_key()
        key_prefix = api_key[:16]

        user_doc = db.users.find_one({"_id": ObjectId(user_id)})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        plan = user_doc.get("plan", "free")
        rate_limits = user_doc.get("limits", {})

        api_key_doc = {
            "key_hash": key_hash,
            "key_prefix": key_prefix,
            "user_id": ObjectId(user_id),
            "organization_id": ObjectId(organization_id) if organization_id else None,
            "name": name,
            "description": description,
            "environment": "production",
            "plan": plan,
            "rate_limits": rate_limits,
            "scopes": None,
            "allowed_models": None,
            "ip_whitelist": None,
            "referrer_whitelist": None,
            "is_active": True,
            "is_test_key": False,
            "usage_count": 0,
            "last_used_at": None,
            "last_used_ip": None,
            "last_used_endpoint": None,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "revoked_at": None,
            "revoked_reason": None,
            "rotated_from": None,
            "rotated_to": None,
            "created_by": ObjectId(user_id),
            "notes": description,
        }

        result = collection.insert_one(api_key_doc)
        api_key_id = str(result.inserted_id)

        logger.info("Created API key for user %s: %s", user_id, key_prefix)

        return {
            "api_key": api_key,
            "api_key_id": api_key_id,
            "key_prefix": key_prefix,
            "created_at": api_key_doc["created_at"].isoformat(),
            "expires_at": expires_at.isoformat() if expires_at else None,
        }

    async def verify_api_key(self, api_key: str) -> Optional[dict[str, Any]]:
        """Verify API key and return user info.

        Args:
            api_key: API key string

        Returns:
            Dictionary with user info if valid, None otherwise
        """
        key_hash = self.hash_api_key(api_key)
        db = mongodb_manager.get_database()
        collection = db.api_keys

        api_key_doc = collection.find_one(
            {
                "key_hash": key_hash,
                "is_active": True,
            }
        )

        if not api_key_doc:
            return None

        if api_key_doc.get("revoked_at"):
            return None

        expires_at = api_key_doc.get("expires_at")
        if expires_at and expires_at < datetime.utcnow():
            return None

        user_id = str(api_key_doc["user_id"])
        organization_id = str(api_key_doc["organization_id"]) if api_key_doc.get("organization_id") else None

        user_doc = db.users.find_one({"_id": api_key_doc["user_id"]})
        if not user_doc:
            logger.warning("User not found for API key: %s", user_id)
            return None

        plan = api_key_doc.get("plan", user_doc.get("plan", "free"))
        rate_limits = api_key_doc.get("rate_limits", user_doc.get("limits", {}))

        return {
            "user_id": user_id,
            "organization_id": organization_id,
            "api_key_id": str(api_key_doc["_id"]),
            "plan": plan,
            "rate_limits": rate_limits,
            "scopes": api_key_doc.get("scopes"),
            "allowed_models": api_key_doc.get("allowed_models"),
        }

    async def revoke_api_key(self, api_key_id: str, user_id: str, reason: Optional[str] = None) -> bool:
        """Revoke API key.

        Args:
            api_key_id: API key ID
            user_id: User ID (for authorization)
            reason: Revocation reason

        Returns:
            True if revoked, False otherwise
        """
        db = mongodb_manager.get_database()
        collection = db.api_keys

        result = collection.update_one(
            {
                "_id": ObjectId(api_key_id),
                "user_id": ObjectId(user_id),
            },
            {
                "$set": {
                    "is_active": False,
                    "revoked_at": datetime.utcnow(),
                    "revoked_reason": reason,
                }
            },
        )

        if result.modified_count > 0:
            logger.info("Revoked API key %s for user %s", api_key_id, user_id)
            return True

        return False

    async def list_api_keys(self, user_id: str) -> list[dict[str, Any]]:
        """List all API keys for user.

        Args:
            user_id: User ID

        Returns:
            List of API key dictionaries
        """
        db = mongodb_manager.get_database()
        collection = db.api_keys

        cursor = collection.find(
            {"user_id": ObjectId(user_id)},
            {
                "key_hash": 0,
            },
        ).sort("created_at", -1)

        keys = []
        async for doc in cursor:
            keys.append({
                "api_key_id": str(doc["_id"]),
                "key_prefix": doc.get("key_prefix"),
                "name": doc.get("name"),
                "description": doc.get("description"),
                "is_active": doc.get("is_active", False),
                "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None,
                "expires_at": doc.get("expires_at").isoformat() if doc.get("expires_at") else None,
                "last_used_at": doc.get("last_used_at").isoformat() if doc.get("last_used_at") else None,
                "usage_count": doc.get("usage_count", 0),
            })

        return keys


api_key_manager = APIKeyManager()


async def verify_api_key(api_key: str) -> bool:
    """Verify API key (legacy function for compatibility).

    Args:
        api_key: API key string

    Returns:
        True if valid, False otherwise
    """
    result = await api_key_manager.verify_api_key(api_key)
    return result is not None


async def get_user_from_api_key(api_key: str) -> Optional[dict[str, Any]]:
    """Get user information from API key.

    Args:
        api_key: API key string

    Returns:
        Dictionary with user info if valid, None otherwise
    """
    return await api_key_manager.verify_api_key(api_key)

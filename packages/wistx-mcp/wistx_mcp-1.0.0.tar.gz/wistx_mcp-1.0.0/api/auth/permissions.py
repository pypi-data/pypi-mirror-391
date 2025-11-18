"""Permission checks for API access."""

import logging
from typing import Any

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


def check_permission(user_info: dict[str, Any], required_permission: str) -> bool:
    """Check if user has required permission.

    Args:
        user_info: User information dictionary
        required_permission: Required permission name

    Returns:
        True if user has permission, False otherwise

    Raises:
        HTTPException: If permission check fails
    """
    plan = user_info.get("plan", "free")
    scopes = user_info.get("scopes", [])

    if required_permission in scopes:
        return True

    plan_permissions = {
        "free": ["read"],
        "starter": ["read", "write"],
        "pro": ["read", "write", "admin"],
        "enterprise": ["read", "write", "admin", "billing"],
    }

    user_permissions = plan_permissions.get(plan, ["read"])

    if required_permission in user_permissions:
        return True

    logger.warning(
        "Permission denied: user %s (plan: %s) attempted %s",
        user_info.get("user_id"),
        plan,
        required_permission,
    )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "error": {
                "code": "PERMISSION_DENIED",
                "message": f"Permission '{required_permission}' required. Current plan: {plan}",
            }
        },
    )


def require_permission(required_permission: str):
    """Decorator to require permission for endpoint.

    Args:
        required_permission: Required permission name

    Returns:
        Decorator function
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            user_info = kwargs.get("current_user")
            if not user_info:
                for arg in args:
                    if isinstance(arg, dict) and "user_id" in arg:
                        user_info = arg
                        break

            if not user_info:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            check_permission(user_info, required_permission)
            return await func(*args, **kwargs)

        return wrapper

    return decorator

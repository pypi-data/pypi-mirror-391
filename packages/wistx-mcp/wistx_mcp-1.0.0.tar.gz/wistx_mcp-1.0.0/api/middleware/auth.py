"""Authentication middleware for FastAPI.

Extracts and validates authentication tokens (API keys or JWT) from requests
and sets user information in request.state for use by route handlers.
"""

import logging
from typing import Callable

from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from api.auth.api_keys import get_user_from_api_key
from api.auth.users import jwt_authentication

logger = logging.getLogger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Authentication middleware that extracts and validates API keys or JWT tokens.

    Sets user information in request.state.user_info for use by route handlers.
    Does not enforce authentication - routes can use get_current_user dependency
    to require authentication.
    """

    def __init__(self, app, enforce_auth: bool = False):
        """Initialize authentication middleware.

        Args:
            app: ASGI application
            enforce_auth: If True, require authentication for all routes (except excluded)
        """
        super().__init__(app)
        self.enforce_auth = enforce_auth
        self.excluded_paths = {
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/auth/",
        }

    def _is_excluded_path(self, path: str) -> bool:
        """Check if path is excluded from authentication.

        Args:
            path: Request path

        Returns:
            True if path is excluded, False otherwise
        """
        return any(path.startswith(excluded) for excluded in self.excluded_paths)

    async def _extract_api_key_user(self, authorization: str) -> dict | None:
        """Extract user info from API key.

        Args:
            authorization: Authorization header value

        Returns:
            User info dictionary or None if invalid
        """
        if not authorization or not authorization.startswith("Bearer "):
            return None

        api_key_value = authorization.replace("Bearer ", "").strip()
        if not api_key_value:
            return None

        try:
            user_info = await get_user_from_api_key(api_key_value)
            return user_info
        except (ValueError, RuntimeError, ConnectionError) as e:
            logger.warning("Failed to verify API key: %s", e)
            return None
        except Exception as e:
            logger.warning("Unexpected error verifying API key: %s", e)
            return None

    async def _extract_jwt_user(self, authorization: str) -> dict | None:
        """Extract user info from JWT token.

        Args:
            authorization: Authorization header value

        Returns:
            User info dictionary or None if invalid
        """
        if not authorization or not authorization.startswith("Bearer "):
            return None

        token = authorization.replace("Bearer ", "").strip()
        if not token:
            return None

        try:
            from fastapi_users.authentication import Authenticator

            strategy = jwt_authentication.get_strategy()
            user = await strategy.read_token(token)
            if user:
                return {
                    "user_id": str(user.id),
                    "plan": getattr(user, "plan", "free"),
                    "rate_limits": getattr(user, "limits", {}),
                }
        except (ValueError, RuntimeError, AttributeError) as e:
            logger.debug("JWT token validation failed: %s", e)
        except Exception as e:
            logger.debug("Unexpected error validating JWT token: %s", e)

        return None

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and extract authentication.

        Args:
            request: FastAPI request object
            call_next: Next middleware/handler

        Returns:
            Response object

        Raises:
            HTTPException: If authentication is required but missing/invalid
        """
        if self._is_excluded_path(request.url.path):
            return await call_next(request)

        authorization = request.headers.get("authorization", "")

        user_info = None

        if authorization:
            user_info = await self._extract_api_key_user(authorization)
            if not user_info:
                user_info = await self._extract_jwt_user(authorization)

        if user_info:
            request.state.user_info = user_info
            logger.debug("Authenticated user: %s", user_info.get("user_id"))
        elif self.enforce_auth:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await call_next(request)

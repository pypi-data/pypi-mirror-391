"""Authentication and API key management endpoints."""

import logging
from datetime import datetime
from typing import Any

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field

from api.auth.api_keys import api_key_manager
from api.auth.users import fastapi_users, jwt_authentication, User
from api.dependencies import get_current_user

get_current_active_user = fastapi_users.current_user(active=True)

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


class CreateAPIKeyRequest(BaseModel):
    """Request model for creating API key."""

    name: str = Field(..., min_length=1, max_length=100, description="API key name")
    description: str | None = Field(default=None, max_length=500, description="API key description")
    expires_at: datetime | None = Field(default=None, description="Expiration date (optional)")


class APIKeyResponse(BaseModel):
    """Response model for API key."""

    api_key: str = Field(..., description="API key (only shown once)")
    api_key_id: str = Field(..., description="API key ID")
    key_prefix: str = Field(..., description="Key prefix for display")
    created_at: str = Field(..., description="Creation timestamp")
    expires_at: str | None = Field(default=None, description="Expiration timestamp")


class APIKeyListResponse(BaseModel):
    """Response model for API key list."""

    api_keys: list[dict[str, Any]] = Field(..., description="List of API keys")


@router.post("/api-keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    request: CreateAPIKeyRequest,
    current_user: User = Depends(get_current_active_user),
) -> APIKeyResponse:
    """Create new API key.

    Requires JWT token from OAuth login.
    """
    user_id = str(current_user.id)

    try:
        organization_id = str(current_user.organization_id) if current_user.organization_id else None
        result = await api_key_manager.create_api_key(
            user_id=user_id,
            name=request.name,
            description=request.description,
            organization_id=organization_id,
            expires_at=request.expires_at,
        )

        return APIKeyResponse(
            api_key=result["api_key"],
            api_key_id=result["api_key_id"],
            key_prefix=result["key_prefix"],
            created_at=result["created_at"],
            expires_at=result.get("expires_at"),
        )
    except Exception as e:
        logger.error("Error creating API key: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create API key",
        ) from e


@router.get("/api-keys", response_model=APIKeyListResponse)
async def list_api_keys(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> APIKeyListResponse:
    """List all API keys for current user."""
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found",
        )

    try:
        keys = await api_key_manager.list_api_keys(user_id=user_id)
        return APIKeyListResponse(api_keys=keys)
    except Exception as e:
        logger.error("Error listing API keys: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list API keys",
        ) from e


@router.delete("/api-keys/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    api_key_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    reason: str | None = None,
) -> None:
    """Revoke API key."""
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found",
        )

    try:
        success = await api_key_manager.revoke_api_key(
            api_key_id=api_key_id,
            user_id=user_id,
            reason=reason,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found or access denied",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error revoking API key: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke API key",
        ) from e


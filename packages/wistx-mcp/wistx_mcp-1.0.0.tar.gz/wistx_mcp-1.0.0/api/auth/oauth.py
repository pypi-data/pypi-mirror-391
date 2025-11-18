"""OAuth routers for Google and GitHub authentication."""

import logging
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from pydantic import SecretStr

from api.auth.users import (
    fastapi_users,
    jwt_authentication,
    google_oauth_client,
    github_oauth_client,
)
from api.config import settings

logger = logging.getLogger(__name__)


def get_oauth_redirect_url(provider: str) -> str:
    """Get OAuth redirect URL for provider.

    Args:
        provider: OAuth provider name (google, github)

    Returns:
        Redirect URL
    """
    if settings.debug:
        base_url = settings.oauth_redirect_url_dev
    else:
        base_url = settings.oauth_redirect_url_prod

    return base_url.format(provider=provider)


oauth_router = APIRouter()


google_oauth_router = fastapi_users.get_oauth_router(
    google_oauth_client,
    jwt_authentication,
    SecretStr(settings.secret_key),
    redirect_url=get_oauth_redirect_url("google"),
    associate_by_email=True,
    is_verified_by_default=True,
)

github_oauth_router = fastapi_users.get_oauth_router(
    github_oauth_client,
    jwt_authentication,
    SecretStr(settings.secret_key),
    redirect_url=get_oauth_redirect_url("github"),
    associate_by_email=True,
    is_verified_by_default=True,
)


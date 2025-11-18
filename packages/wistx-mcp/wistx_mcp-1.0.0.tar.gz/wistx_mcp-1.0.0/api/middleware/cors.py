"""CORS middleware for FastAPI."""

from fastapi import Request
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp

from api.config import settings


def setup_cors_middleware(app: ASGIApp) -> None:
    """Setup CORS middleware.

    Args:
        app: FastAPI application
    """
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://app.wistx.ai",
        "https://wistx.ai",
    ]

    if settings.debug:
        allowed_origins.extend([
            "http://localhost:*",
            "http://127.0.0.1:*",
        ])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Window"],
    )

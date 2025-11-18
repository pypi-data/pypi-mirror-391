"""Rate limiting middleware for FastAPI with Redis and plan-based limits."""

import logging
import time
from collections import defaultdict, deque
from typing import Any, Callable, Optional

from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from api.config import settings
from api.services.plan_service import plan_service

logger = logging.getLogger(__name__)

_redis_client: Optional[Any] = None


def get_redis_client():
    """Get Redis client (lazy initialization).

    Returns:
        Redis client or None if Redis not configured
    """
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    if not settings.redis_url:
        return None

    try:
        import redis.asyncio as redis

        _redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        logger.info("Redis client initialized for distributed rate limiting")
        return _redis_client
    except ImportError:
        logger.warning(
            "Redis not installed. Install with: pip install redis. Falling back to in-memory rate limiting."
        )
        return None
    except Exception as e:
        logger.warning("Failed to initialize Redis client: %s. Falling back to in-memory rate limiting.", e)
        return None


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with Redis support and plan-based limits.

    Supports both in-memory (single instance) and Redis-based (distributed) rate limiting.
    Uses plan-based limits from plan_service.
    """

    def __init__(self, app: ASGIApp, requests_per_minute: int | None = None):
        """Initialize rate limiting middleware.

        Args:
            app: ASGI application
            requests_per_minute: Default requests per minute (fallback if plan not found)
        """
        super().__init__(app)
        self.default_requests_per_minute = requests_per_minute or settings.rate_limit_requests_per_minute
        self.window_seconds = 60
        self.request_times: dict[str, deque[float]] = defaultdict(self._create_deque)
        self.redis_client = get_redis_client()
        self.use_redis = self.redis_client is not None

    @staticmethod
    def _create_deque() -> deque[float]:
        """Create a new deque for rate limiting."""
        return deque()

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting.

        Args:
            request: FastAPI request object

        Returns:
            Client identifier (user_id if available, otherwise IP or API key)
        """
        user_info = getattr(request.state, "user_info", None)
        if user_info and user_info.get("user_id"):
            return f"user:{user_info['user_id']}"

        client_ip = request.client.host if request.client else "unknown"

        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            api_key = auth_header.replace("Bearer ", "")
            return f"api_key:{api_key[:16]}"

        return f"ip:{client_ip}"

    def _get_plan_limit(self, request: Request) -> int:
        """Get rate limit for user's plan.

        Args:
            request: FastAPI request object

        Returns:
            Requests per minute limit
        """
        user_info = getattr(request.state, "user_info", None)
        if user_info:
            plan = user_info.get("plan", "free")
            plan_limits = plan_service.get_plan_limits(plan)
            if plan_limits:
                return plan_limits.requests_per_minute

        return self.default_requests_per_minute

    def _is_rate_limited_in_memory(self, client_id: str, limit: int) -> bool:
        """Check if client is rate limited (in-memory).

        Args:
            client_id: Client identifier
            limit: Requests per minute limit

        Returns:
            True if rate limited, False otherwise
        """
        now = time.time()
        window_start = now - self.window_seconds

        request_times = self.request_times[client_id]

        while request_times and request_times[0] < window_start:
            request_times.popleft()

        if len(request_times) >= limit:
            return True

        request_times.append(now)
        return False

    async def _is_rate_limited_redis(self, client_id: str, limit: int) -> bool:
        """Check if client is rate limited (Redis).

        Args:
            client_id: Client identifier
            limit: Requests per minute limit

        Returns:
            True if rate limited, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            key = f"rate_limit:{client_id}"
            now = time.time()
            window_start = now - self.window_seconds

            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, self.window_seconds + 10)

            results = await pipe.execute()
            current_count = results[1] if len(results) > 1 else 0

            if current_count >= limit:
                return True

            return False
        except Exception as e:
            logger.warning("Redis rate limit check failed: %s. Falling back to in-memory.", e)
            return self._is_rate_limited_in_memory(client_id, limit)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting.

        Args:
            request: FastAPI request object
            call_next: Next middleware/handler

        Returns:
            Response object

        Raises:
            HTTPException: If rate limit exceeded
        """
        if request.url.path.startswith("/health") or request.url.path.startswith("/docs"):
            return await call_next(request)

        client_id = self._get_client_id(request)
        limit = self._get_plan_limit(request)

        is_limited = False
        if self.use_redis:
            is_limited = await self._is_rate_limited_redis(client_id, limit)
        else:
            is_limited = self._is_rate_limited_in_memory(client_id, limit)

        if is_limited:
            logger.warning(
                "Rate limit exceeded for client: %s (limit: %d/min) | Path: %s",
                client_id,
                limit,
                request.url.path,
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Rate limit exceeded. Maximum {limit} requests per minute.",
                        "details": {
                            "limit": limit,
                            "window_seconds": self.window_seconds,
                        },
                    }
                },
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Window": str(self.window_seconds),
                    "Retry-After": str(self.window_seconds),
                },
            )

        response = await call_next(request)

        remaining = limit
        if self.use_redis:
            try:
                key = f"rate_limit:{client_id}"
                count = await self.redis_client.zcard(key)
                remaining = max(0, limit - count)
            except Exception:
                remaining = limit - 1
        else:
            remaining = max(0, limit - len(self.request_times[client_id]))

        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Window"] = str(self.window_seconds)

        return response

"""FastAPI main application."""

import logging
from typing import Any

from fastapi import FastAPI

from api.config import settings
from api.middleware.logging import setup_logging_middleware
from api.middleware.rate_limit import RateLimitMiddleware
from api.middleware.token_tracking import UsageTrackingMiddleware
from api.middleware.cors import setup_cors_middleware
from api.middleware.request_size_limit import RequestSizeLimitMiddleware

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.getLogger("pymongo.connection").setLevel(logging.WARNING)
logging.getLogger("pymongo.topology").setLevel(logging.WARNING)
logging.getLogger("pymongo.serverSelection").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.api_title,
    description="WISTX API - REST endpoints for compliance, pricing, and code examples context",
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.debug,
)

setup_logging_middleware(app)
setup_cors_middleware(app)
app.add_middleware(RequestSizeLimitMiddleware, max_request_size_mb=getattr(settings, "max_request_size_mb", 10))
app.add_middleware(RateLimitMiddleware)
app.add_middleware(UsageTrackingMiddleware)

logger.info("Starting WISTX API v%s", settings.api_version)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize database collections on startup."""
    from api.database.mongodb import mongodb_manager
    from api.database.exceptions import MongoDBConnectionError
    from pymongo.errors import (
        ServerSelectionTimeoutError,
        NetworkTimeout,
        ConnectionFailure,
        OperationFailure,
    )

    try:
        logger.info("Initializing MongoDB collections...")
        db = mongodb_manager.get_database()

        collections = [
            "compliance_controls",
            "pricing_data",
            "code_examples",
            "best_practices",
            "knowledge_articles",
            "users",
            "api_keys",
            "api_usage",
            "user_usage_summary",
            "indexed_resources",
            "reports",
        ]

        created_count = 0
        for collection_name in collections:
            try:
                if collection_name not in db.list_collection_names():
                    db.create_collection(collection_name)
                    logger.info("Created collection: %s", collection_name)
                    created_count += 1
            except OperationFailure as e:
                if "already exists" in str(e).lower() or "namespace exists" in str(e).lower():
                    logger.debug("Collection %s already exists (race condition)", collection_name)
                else:
                    logger.warning("Failed to create collection %s: %s", collection_name, e)

        if created_count > 0:
            logger.info("Created %d new MongoDB collections", created_count)
        else:
            logger.info("All MongoDB collections already exist")

        logger.info("Note: Run 'python scripts/setup_mongodb.py' to create indexes")
    except (
        MongoDBConnectionError,
        ServerSelectionTimeoutError,
        NetworkTimeout,
        ConnectionFailure,
        ConnectionError,
        TimeoutError,
        ValueError,
    ) as e:
        logger.warning("Failed to initialize MongoDB collections: %s", e)
        logger.warning("Collections may need to be created manually via: python scripts/setup_mongodb.py")
        logger.warning("API will continue to start, but database operations may fail")

    if settings.pinecone_api_key:
        logger.info("Initializing Pinecone connection...")
        try:
            from pinecone import Pinecone  # type: ignore[import-untyped]
            from pinecone.exceptions import NotFoundException  # type: ignore[import-untyped]
        except (ImportError, ModuleNotFoundError) as import_error:
            error_msg = str(import_error)
            if "pinecone-client" in error_msg.lower() or "renamed" in error_msg.lower():
                logger.warning(
                    "Pinecone package conflict detected. Please uninstall 'pinecone-client' "
                    "and install 'pinecone' instead: pip uninstall pinecone-client && pip install pinecone"
                )
            else:
                logger.warning("Pinecone client not installed. Install with: pip install pinecone")
            logger.warning("Vector search features will not be available")
        else:
            try:
                pc = Pinecone(api_key=settings.pinecone_api_key)
                index_name = settings.pinecone_index_name

                try:
                    existing_indexes = pc.list_indexes().names()
                    if index_name not in existing_indexes:
                        logger.info("Creating Pinecone index '%s'...", index_name)
                        try:
                            pc.create_index(
                                name=index_name,
                                dimension=settings.pinecone_index_dimension,
                                metric="cosine",
                                spec={
                                    "serverless": {
                                        "cloud": "aws",
                                        "region": settings.pinecone_index_region,
                                    }
                                },
                            )
                            logger.info("Successfully created Pinecone index '%s'", index_name)
                            logger.info("Note: Index creation may take a few minutes to complete")
                        except (ValueError, RuntimeError, ConnectionError) as create_error:
                            error_msg = str(create_error)
                            if "already exists" in error_msg.lower() or "already exist" in error_msg.lower():
                                logger.info("Pinecone index '%s' already exists (created concurrently)", index_name)
                            else:
                                logger.warning("Failed to create Pinecone index '%s': %s", index_name, create_error)
                                raise
                    else:
                        logger.info("Pinecone index '%s' already exists", index_name)

                    index = pc.Index(index_name)
                    stats = index.describe_index_stats()
                    logger.info(
                        "Successfully connected to Pinecone: index '%s' (%d vectors)",
                        index_name,
                        stats.get("total_vector_count", 0),
                    )
                except NotFoundException:
                    logger.warning(
                        "Pinecone index '%s' not found after creation attempt",
                        index_name,
                    )
                    logger.warning("Vector search features will not be available until index is ready")
                except (ConnectionError, TimeoutError, ValueError, AttributeError) as index_error:
                    logger.warning(
                        "Pinecone index '%s' not accessible: %s",
                        index_name,
                        index_error,
                    )
                    logger.warning("Vector search features will not be available")
            except (ValueError, RuntimeError, ConnectionError, TimeoutError) as e:
                logger.warning("Failed to initialize Pinecone: %s", e)
                logger.warning("Vector search features will not be available")
    else:
        logger.info("Pinecone not configured (PINECONE_API_KEY not set)")


@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    from api.database.mongodb import mongodb_manager

    health_status = {
        "status": "healthy",
        "api": {
            "version": settings.api_version,
            "title": settings.api_title,
        },
    }

    try:
        db_health = mongodb_manager.health_check()
        health_status["database"] = {
            "status": db_health.get("status", "unknown"),
            "latency_ms": db_health.get("latency_ms"),
            "connections": db_health.get("connections", {}),
        }
    except (ConnectionError, TimeoutError, ValueError) as e:
        health_status["database"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        health_status["status"] = "degraded"

    if settings.pinecone_api_key:
        try:
            try:
                from pinecone import Pinecone  # type: ignore[import-untyped]
                from pinecone.exceptions import NotFoundException  # type: ignore[import-untyped]
            except (ImportError, ModuleNotFoundError) as import_error:
                error_msg = str(import_error)
                if "pinecone-client" in error_msg.lower() or "renamed" in error_msg.lower():
                    health_status["pinecone"] = {
                        "status": "unavailable",
                        "error": "Package conflict: uninstall 'pinecone-client' and install 'pinecone'",
                    }
                else:
                    health_status["pinecone"] = {
                        "status": "unavailable",
                        "error": f"Import error: {import_error}",
                    }
            else:
                try:
                    pc = Pinecone(api_key=settings.pinecone_api_key)
                    index = pc.Index(settings.pinecone_index_name)
                    stats = index.describe_index_stats()
                    health_status["pinecone"] = {
                        "status": "healthy",
                        "index": settings.pinecone_index_name,
                        "vector_count": stats.get("total_vector_count", 0),
                    }
                except NotFoundException:
                    health_status["pinecone"] = {
                        "status": "index_not_found",
                        "error": f"Index '{settings.pinecone_index_name}' does not exist. Run 'python scripts/setup_pinecone.py' to create it",
                    }
                    if health_status["status"] == "healthy":
                        health_status["status"] = "degraded"
                except (ConnectionError, TimeoutError, ValueError, AttributeError) as e:
                    health_status["pinecone"] = {
                        "status": "unhealthy",
                        "error": str(e),
                    }
                    if health_status["status"] == "healthy":
                        health_status["status"] = "degraded"
        except (ValueError, RuntimeError, ConnectionError, TimeoutError) as e:
            health_status["pinecone"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            if health_status["status"] == "healthy":
                health_status["status"] = "degraded"
    else:
        health_status["pinecone"] = {
            "status": "not_configured",
        }

    return health_status


from api.routers.v1 import router as v1_router
from api.routers.internal import webhooks
from api.auth.oauth import google_oauth_router, github_oauth_router
from api.auth.users import fastapi_users, jwt_authentication

app.include_router(v1_router, prefix="/v1", tags=["v1"])
app.include_router(webhooks.router, prefix="/internal", tags=["internal"])

app.include_router(
    google_oauth_router,
    prefix="/auth/google",
    tags=["auth"],
)

app.include_router(
    github_oauth_router,
    prefix="/auth/github",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_auth_router(jwt_authentication),
    prefix="/auth/jwt",
    tags=["auth"],
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)


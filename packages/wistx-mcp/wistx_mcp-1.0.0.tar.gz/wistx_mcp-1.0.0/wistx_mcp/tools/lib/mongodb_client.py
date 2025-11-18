"""MongoDB client for MCP tools."""

import asyncio
import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from wistx_mcp.config import settings

logger = logging.getLogger(__name__)


class MongoDBClient:
    """MongoDB client wrapper for MCP tools with connection pooling and retry logic."""

    def __init__(self):
        """Initialize MongoDB client."""
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self._max_retries = 3
        self._retry_delay = 1.0

    async def connect(self) -> None:
        """Connect to MongoDB with proper connection management.

        Includes:
        - Connection pooling (max 50, min 10)
        - Retry logic for transient failures
        - Health checks with timeout
        - Connection string validation

        Raises:
            RuntimeError: If connection fails after retries
        """
        if self.client is None:
            connection_string = str(settings.mongodb_url).strip().rstrip("/")
            
            if not connection_string:
                raise ValueError("MongoDB connection string is required")

            try:
                from api.config import settings as api_settings

                motor_options = {
                    "maxPoolSize": api_settings.mongodb_max_pool_size,
                    "minPoolSize": api_settings.mongodb_min_pool_size,
                    "maxIdleTimeMS": api_settings.mongodb_max_idle_time_ms,
                    "serverSelectionTimeoutMS": api_settings.mongodb_server_selection_timeout_ms,
                    "connectTimeoutMS": api_settings.mongodb_connect_timeout_ms,
                    "socketTimeoutMS": api_settings.mongodb_socket_timeout_ms,
                    "retryWrites": api_settings.mongodb_retry_writes,
                    "retryReads": True,
                    "heartbeatFrequencyMS": api_settings.mongodb_heartbeat_frequency_ms,
                }

                read_pref_map = {
                    "primary": "primary",
                    "primarypreferred": "primaryPreferred",
                    "secondary": "secondary",
                    "secondarypreferred": "secondaryPreferred",
                    "nearest": "nearest",
                }
                read_pref_str = api_settings.mongodb_read_preference.lower()
                motor_options["readPreference"] = read_pref_map.get(read_pref_str, "secondaryPreferred")

                self.client = AsyncIOMotorClient(connection_string, **motor_options)
                self.database = self.client[settings.mongodb_database]

                for attempt in range(self._max_retries):
                    try:
                        await asyncio.wait_for(
                            self.client.admin.command("ping"),
                            timeout=5.0,
                        )
                        logger.info("Connected to MongoDB: %s", settings.mongodb_database)
                        return
                    except asyncio.TimeoutError:
                        if attempt < self._max_retries - 1:
                            logger.warning(
                                "MongoDB ping timeout (attempt %d/%d), retrying...",
                                attempt + 1,
                                self._max_retries,
                            )
                            await asyncio.sleep(self._retry_delay * (attempt + 1))
                        else:
                            raise RuntimeError("MongoDB connection timeout after retries")
                    except (asyncio.TimeoutError, ConnectionError, RuntimeError) as e:
                        if attempt < self._max_retries - 1:
                            logger.warning(
                                "MongoDB connection error (attempt %d/%d): %s, retrying...",
                                attempt + 1,
                                self._max_retries,
                                e,
                            )
                            await asyncio.sleep(self._retry_delay * (attempt + 1))
                        else:
                            raise RuntimeError(f"Failed to connect to MongoDB after retries: {e}") from e

            except (ValueError, RuntimeError, ConnectionError) as e:
                logger.error("Failed to initialize MongoDB client: %s", e, exc_info=True)
                if self.client:
                    self.client.close()
                    self.client = None
                raise RuntimeError(f"Failed to initialize MongoDB client: {e}") from e

    async def disconnect(self) -> None:
        """Disconnect from MongoDB and clean up resources."""
        if self.client:
            try:
                self.client.close()
                logger.debug("MongoDB client disconnected")
            except (RuntimeError, ConnectionError) as e:
                logger.warning("Error closing MongoDB client: %s", e)
            finally:
                self.client = None
                self.database = None

    async def health_check(self) -> bool:
        """Perform health check on MongoDB connection.

        Returns:
            True if connection is healthy, False otherwise
        """
        if not self.client or not self.database:
            return False

        try:
            await asyncio.wait_for(
                self.client.admin.command("ping"),
                timeout=2.0,
            )
            return True
        except (asyncio.TimeoutError, ConnectionError, RuntimeError) as e:
            logger.warning("MongoDB health check failed: %s", e)
            return False


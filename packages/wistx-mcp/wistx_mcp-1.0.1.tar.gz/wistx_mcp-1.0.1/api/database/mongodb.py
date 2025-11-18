"""Production-ready MongoDB connection manager."""

import logging
import atexit
from typing import Any, Optional
from contextlib import contextmanager

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import (
    ServerSelectionTimeoutError,
    NetworkTimeout,
    ConnectionFailure,
    AutoReconnect,
    NotPrimaryError,
    ExecutionTimeout,
)

from api.config import settings
from api.database.exceptions import (
    MongoDBConnectionError,
    MongoDBCircuitBreakerOpenError,
)
from api.database.circuit_breaker import CircuitBreaker
from api.database.retry_handler import retry_mongodb_operation
from api.database.health_check import MongoDBHealthCheck

logger = logging.getLogger(__name__)


class MongoDBManager:
    """Production-ready MongoDB connection manager.

    Features:
    - Connection pooling
    - Automatic reconnection
    - Retry logic with exponential backoff
    - Circuit breaker pattern
    - Health checks
    - Graceful shutdown
    - Context manager support
    """

    _instance: Optional["MongoDBManager"] = None
    _client: Optional[MongoClient] = None

    def __new__(cls) -> "MongoDBManager":
        """Singleton pattern - ensure only one instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize MongoDB manager."""
        if self._client is not None:
            return

        self._client: Optional[MongoClient] = None
        self._database: Optional[Database] = None
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=settings.mongodb_circuit_breaker_failure_threshold,
            recovery_timeout=settings.mongodb_circuit_breaker_recovery_timeout,
            expected_exception=(
                ServerSelectionTimeoutError,
                NetworkTimeout,
                ConnectionFailure,
                AutoReconnect,
                NotPrimaryError,
                ExecutionTimeout,
            ),
            name="mongodb",
        )
        self._health_check: Optional[MongoDBHealthCheck] = None

        atexit.register(self.close)

    def connect(self) -> MongoClient:
        """Connect to MongoDB with production-ready configuration.

        Returns:
            MongoDB client instance

        Raises:
            MongoDBConnectionError: If connection fails
        """
        if self._client is not None:
            return self._client

        try:
            connection_string = self._build_connection_string()

            logger.info("Connecting to MongoDB...")

            options = settings.get_mongodb_connection_options()

            self._client = MongoClient(connection_string, **options)

            self._test_connection()

            self._database = self._client[settings.mongodb_database]

            self._health_check = MongoDBHealthCheck(self._client)

            logger.info(
                "Successfully connected to MongoDB: %s (pool size: %s)",
                settings.mongodb_database,
                options["maxPoolSize"],
            )

            return self._client

        except Exception as e:
            logger.error("Failed to connect to MongoDB: %s", e)
            raise MongoDBConnectionError(f"Failed to connect to MongoDB: {e}") from e

    def _build_connection_string(self) -> str:
        """Build MongoDB connection string with all options.

        Returns:
            Complete connection string (without database name - handled separately)
        """
        connection_url = str(settings.mongodb_url).strip()

        connection_url = connection_url.rstrip("/")


        return connection_url

    @retry_mongodb_operation(
        max_attempts=settings.mongodb_retry_max_attempts,
        initial_delay=settings.mongodb_retry_initial_delay,
        max_delay=settings.mongodb_retry_max_delay,
    )
    def _test_connection(self) -> None:
        """Test MongoDB connection.

        Raises:
            MongoDBConnectionError: If connection test fails
        """
        if self._client is None:
            raise MongoDBConnectionError("Client not initialized")

        self._client.admin.command("ping")

    def get_client(self) -> MongoClient:
        """Get MongoDB client instance.

        Returns:
            MongoDB client

        Raises:
            MongoDBConnectionError: If not connected
        """
        if self._client is None:
            self.connect()

        if self._client is None:
            raise MongoDBConnectionError("Failed to initialize MongoDB client")

        return self._client

    def get_database(self) -> Database:
        """Get MongoDB database instance.

        Returns:
            MongoDB database

        Raises:
            MongoDBConnectionError: If not connected
        """
        if self._database is None:
            self.connect()

        if self._database is None:
            raise MongoDBConnectionError("Failed to initialize MongoDB database")

        return self._database

    @contextmanager
    def safe_operation(self):
        """Context manager for safe MongoDB operations with circuit breaker.

        Usage:
            with mongodb_manager.safe_operation():
                db.collection.find_one(...)
        """
        try:
            if self._circuit_breaker.get_state().value == "open":
                raise MongoDBCircuitBreakerOpenError()

            yield self._circuit_breaker

        except (
            ServerSelectionTimeoutError,
            NetworkTimeout,
            ConnectionFailure,
            AutoReconnect,
            NotPrimaryError,
            ExecutionTimeout,
        ) as e:
            self._circuit_breaker.call(lambda: None)
            raise MongoDBConnectionError(f"MongoDB operation failed: {e}") from e

    def health_check(self) -> dict[str, Any]:
        """Perform health check.

        Returns:
            Health status dictionary

        Raises:
            MongoDBConnectionError: If health check fails
        """
        if self._health_check is None:
            self.connect()

        if self._health_check is None:
            raise MongoDBConnectionError("Health check not initialized")

        return self._circuit_breaker.call(self._health_check.check)

    def is_healthy(self) -> bool:
        """Check if MongoDB is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            status = self.health_check()
            return status.get("status") == "healthy"
        except (MongoDBConnectionError, MongoDBCircuitBreakerOpenError):
            return False

    def get_circuit_breaker_stats(self) -> dict[str, Any]:
        """Get circuit breaker statistics.

        Returns:
            Circuit breaker statistics
        """
        return self._circuit_breaker.get_stats()

    def reset_circuit_breaker(self) -> None:
        """Manually reset circuit breaker."""
        self._circuit_breaker.reset()

    def close(self) -> None:
        """Close MongoDB connection gracefully."""
        if self._client is not None:
            logger.info("Closing MongoDB connection...")
            try:
                self._client.close()
                logger.info("MongoDB connection closed")
            except Exception as e:
                logger.error("Error closing MongoDB connection: %s", e)
            finally:
                self._client = None
                self._database = None
                self._health_check = None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""


mongodb_manager = MongoDBManager()


def get_database() -> Database:
    """Get MongoDB database instance (dependency injection helper).

    Returns:
        MongoDB database instance
    """
    return mongodb_manager.get_database()


def get_client() -> MongoClient:
    """Get MongoDB client instance (dependency injection helper).

    Returns:
        MongoDB client instance
    """
    return mongodb_manager.get_client()

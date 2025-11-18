"""Configuration settings.

All settings are loaded from environment variables (.env file).
Required variables must be set in .env file.

Example .env file:
    MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/
    MONGODB_DATABASE=wistx-production
"""

from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    All settings are loaded from environment variables (.env file).
    The .env file should be in the project root directory.
    """

    api_title: str = "WISTX API"
    api_version: str = "0.1.0"
    debug: bool = False

    mongodb_url: str = Field(
        ...,
        validation_alias="MONGODB_URI",
        description="MongoDB connection URL. Must be set in .env file as MONGODB_URI.",
        examples=[
            "mongodb+srv://user:pass@cluster.mongodb.net/",
            "mongodb://localhost:27017",
        ],
    )
    mongodb_database: str = Field(
        default="wistx",
        validation_alias="DATABASE_NAME",
        description="MongoDB database name",
    )

    mongodb_max_pool_size: int = 50
    mongodb_min_pool_size: int = 10
    mongodb_max_idle_time_ms: int = 30000
    mongodb_server_selection_timeout_ms: int = 5000
    mongodb_connect_timeout_ms: int = 10000
    mongodb_socket_timeout_ms: int = 60000
    mongodb_heartbeat_frequency_ms: int = 10000
    mongodb_retry_writes: bool = True
    mongodb_read_preference: str = "secondaryPreferred"

    mongodb_circuit_breaker_failure_threshold: int = 5
    mongodb_circuit_breaker_recovery_timeout: int = 60

    mongodb_retry_max_attempts: int = 3
    mongodb_retry_initial_delay: float = 1.0
    mongodb_retry_max_delay: float = 10.0

    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_server_url: str = "http://localhost:8001"

    rate_limit_requests_per_minute: int = 60
    rate_limit_tokens_per_day: int = 1000000

    redis_url: str | None = Field(
        default=None,
        validation_alias="REDIS_URL",
        description="Redis URL for distributed rate limiting (optional, defaults to in-memory if not set)",
        examples=["redis://localhost:6379", "redis://user:pass@localhost:6379/0"],
    )

    pinecone_api_key: str | None = Field(
        default=None,
        validation_alias="PINECONE_API_KEY",
        description="Pinecone API key (optional, required for vector search)",
    )
    pinecone_environment: str | None = Field(
        default=None,
        validation_alias="PINECONE_ENVIRONMENT",
        description="Pinecone environment/region (optional)",
    )
    pinecone_index_name: str = Field(
        default="wistx",
        validation_alias="PINECONE_INDEX_NAME",
        description="Pinecone index name",
    )
    pinecone_index_dimension: int = Field(
        default=1536,
        validation_alias="PINECONE_INDEX_DIMENSION",
        description="Pinecone index dimension (1536 for OpenAI text-embedding-3-small)",
    )
    pinecone_index_region: str = Field(
        default="us-east-1",
        validation_alias="PINECONE_INDEX_REGION",
        description="Pinecone index region (for serverless indexes)",
    )

    openai_api_key: str = Field(
        ...,
        validation_alias="OPENAI_API_KEY",
        description="OpenAI API key for embeddings",
    )

    google_oauth_client_id: str = Field(
        ...,
        validation_alias="GOOGLE_OAUTH_CLIENT_ID",
        description="Google OAuth 2.0 client ID",
    )
    google_oauth_client_secret: str = Field(
        ...,
        validation_alias="GOOGLE_OAUTH_CLIENT_SECRET",
        description="Google OAuth 2.0 client secret",
    )
    github_oauth_client_id: str = Field(
        ...,
        validation_alias="GITHUB_OAUTH_CLIENT_ID",
        description="GitHub OAuth app client ID",
    )
    github_oauth_client_secret: str = Field(
        ...,
        validation_alias="GITHUB_OAUTH_CLIENT_SECRET",
        description="GitHub OAuth app client secret",
    )
    oauth_redirect_url_dev: str = Field(
        default="http://localhost:8000/auth/{provider}/callback",
        validation_alias="OAUTH_REDIRECT_URL_DEV",
        description="OAuth redirect URL for development",
    )
    oauth_redirect_url_prod: str = Field(
        default="https://api.wistx.ai/auth/{provider}/callback",
        validation_alias="OAUTH_REDIRECT_URL_PROD",
        description="OAuth redirect URL for production",
    )

    stripe_secret_key: str | None = Field(
        default=None,
        validation_alias="STRIPE_SECRET_KEY",
        description="Stripe secret key for billing",
    )
    stripe_publishable_key: str | None = Field(
        default=None,
        validation_alias="STRIPE_PUBLISHABLE_KEY",
        description="Stripe publishable key for frontend",
    )
    stripe_webhook_secret: str | None = Field(
        default=None,
        validation_alias="STRIPE_WEBHOOK_SECRET",
        description="Stripe webhook secret for verifying webhooks",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("mongodb_url")
    @classmethod
    def validate_mongodb_url(cls, v: str) -> str:
        """Validate MongoDB URL is set and not using default localhost in production."""
        if not v or v.strip() == "":
            raise ValueError(
                "MONGODB_URL is required. Please set it in your .env file.\n"
                "Example: MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/"
            )

        if v == "mongodb://localhost:27017":
            import warnings

            warnings.warn(
                "Using default MongoDB URL (localhost). "
                "Make sure MONGODB_URL is set in your .env file.",
                UserWarning,
            )

        return v.strip()

    def get_mongodb_connection_options(self) -> dict[str, Any]:
        """Get MongoDB connection options as dictionary.

        Returns:
            Dictionary of MongoDB connection options
        """
        mongodb_url_str = str(self.mongodb_url)
        is_atlas = mongodb_url_str.startswith("mongodb+srv://")

        read_pref_map = {
            "primary": "primary",
            "primarypreferred": "primaryPreferred",
            "secondary": "secondary",
            "secondarypreferred": "secondaryPreferred",
            "nearest": "nearest",
        }

        read_pref_str = self.mongodb_read_preference.lower()
        read_preference = read_pref_map.get(read_pref_str, "secondaryPreferred")

        options = {
            "maxPoolSize": self.mongodb_max_pool_size,
            "minPoolSize": self.mongodb_min_pool_size,
            "maxIdleTimeMS": self.mongodb_max_idle_time_ms,
            "serverSelectionTimeoutMS": self.mongodb_server_selection_timeout_ms,
            "connectTimeoutMS": self.mongodb_connect_timeout_ms,
            "socketTimeoutMS": self.mongodb_socket_timeout_ms,
            "heartbeatFrequencyMS": self.mongodb_heartbeat_frequency_ms,
            "retryWrites": self.mongodb_retry_writes,
            "readPreference": read_preference,
            "appName": "wistx-api",
            "compressors": ["zlib"],
        }

        if is_atlas:
            options["tls"] = True
            options["tlsAllowInvalidCertificates"] = False

        return options


settings = Settings()

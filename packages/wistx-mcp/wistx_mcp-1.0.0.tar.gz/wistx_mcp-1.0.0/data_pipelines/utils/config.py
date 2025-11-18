"""Configuration settings for data pipelines."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PipelineSettings(BaseSettings):
    """Pipeline configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    mongodb_uri: str = Field(
        ...,
        validation_alias="MONGODB_URI",
        description="MongoDB connection URI",
    )
    mongodb_db_name: str = Field(
        default="wistx-production",
        validation_alias="DATABASE_NAME",
        description="MongoDB database name",
    )

    openai_api_key: str = Field(
        ...,
        validation_alias="OPENAI_API_KEY",
        description="OpenAI API key for embeddings",
    )

    pinecone_api_key: str = Field(
        ...,
        validation_alias="PINECONE_API_KEY",
        description="Pinecone API key",
    )

    pinecone_environment: str = Field(
        default="us-east-1-aws",
        validation_alias="PINECONE_ENVIRONMENT",
        description="Pinecone environment/region",
    )

    pinecone_index_name: str = Field(
        default="wistx",
        validation_alias="PINECONE_INDEX_NAME",
        description="Pinecone index name",
    )

    github_token: str | None = Field(
        default=None,
        validation_alias="GITHUB_TOKEN",
        description="GitHub token for API access",
    )

    aws_access_key_id: str | None = Field(
        default=None,
        validation_alias="AWS_ACCESS_KEY_ID",
        description="AWS access key ID for pricing API",
    )
    aws_secret_access_key: str | None = Field(
        default=None,
        validation_alias="AWS_SECRET_ACCESS_KEY",
        description="AWS secret access key",
    )

    max_workers: int = Field(
        default=4,
        description="Maximum number of worker threads",
    )
    batch_size: int = Field(
        default=1000,
        description="Batch size for processing",
    )
    retry_attempts: int = Field(
        default=3,
        description="Number of retry attempts",
    )
    retry_delay: int = Field(
        default=5,
        description="Retry delay in seconds",
    )

    streaming_batch_size: int = Field(
        default=10,
        validation_alias="STREAMING_BATCH_SIZE",
        description="Batch size for streaming saves (progress logging)",
    )

    embedding_batch_size: int = Field(
        default=20,
        validation_alias="EMBEDDING_BATCH_SIZE",
        description="Batch size for embedding generation",
    )

    data_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent / "data",
        description="Base directory for data files",
    )


settings = PipelineSettings()


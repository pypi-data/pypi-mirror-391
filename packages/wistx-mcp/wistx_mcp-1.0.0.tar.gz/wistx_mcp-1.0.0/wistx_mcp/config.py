"""MCP server configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MCPServerSettings(BaseSettings):
    """MCP server configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    mongodb_url: str = Field(
        ...,
        validation_alias="MONGODB_URI",
        description="MongoDB connection URL",
    )

    mongodb_database: str = Field(
        default="wistx-production",
        validation_alias="DATABASE_NAME",
        description="MongoDB database name",
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

    server_name: str = Field(
        default="wistx-mcp",
        description="MCP server name",
    )

    server_version: str = Field(
        default="0.1.0",
        description="MCP server version",
    )

    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )

    api_key: str | None = Field(
        default=None,
        validation_alias="WISTX_API_KEY",
        description="WISTX API key for REST API calls",
    )

    api_url: str = Field(
        default="http://localhost:8000",
        validation_alias="WISTX_API_URL",
        description="WISTX API base URL",
    )

    openai_api_key: str | None = Field(
        default=None,
        validation_alias="OPENAI_API_KEY",
        description="OpenAI API key for embeddings",
    )

    tavily_api_key: str | None = Field(
        default=None,
        validation_alias="TAVILY_API_KEY",
        description="Tavily API key for web search",
    )

    tavily_max_age_days: int = Field(
        default=90,
        validation_alias="TAVILY_MAX_AGE_DAYS",
        description="Maximum age of web search results in days (default: 90 days for DevOps/infrastructure)",
    )


settings = MCPServerSettings()


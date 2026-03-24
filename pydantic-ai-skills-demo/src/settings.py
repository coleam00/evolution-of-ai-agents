"""Settings configuration for Skill-Based Agent."""

from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from dotenv import load_dotenv
from typing import Optional, Literal

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Skills Configuration
    skills_dir: Path = Field(
        default=Path("skills"),
        description="Directory containing skill definitions"
    )

    # LLM Configuration (OpenAI-compatible)
    llm_provider: Literal["openrouter", "openai", "ollama"] = Field(
        default="openrouter",
        description="LLM provider to use"
    )

    llm_api_key: str = Field(..., description="API key for the LLM provider")

    llm_model: str = Field(
        default="anthropic/claude-sonnet-4.5",
        description="Model to use for agent",
    )

    llm_base_url: Optional[str] = Field(
        default="https://openrouter.ai/api/v1",
        description="Base URL for the LLM API (for OpenAI-compatible providers)",
    )

    # OpenRouter-Specific (Optional)
    openrouter_app_url: Optional[str] = Field(
        default=None,
        description="App URL for OpenRouter analytics (optional)"
    )
    openrouter_app_title: Optional[str] = Field(
        default=None,
        description="App title for OpenRouter tracking (optional)"
    )

    # Application Settings
    app_env: str = Field(default="development", description="Application environment")
    log_level: str = Field(default="INFO", description="Logging level")

    # Logfire (Optional)
    logfire_token: Optional[str] = Field(
        default=None,
        description="Logfire API token from 'logfire auth' (optional)"
    )
    logfire_service_name: str = Field(
        default="skill-agent",
        description="Service name in Logfire"
    )
    logfire_environment: str = Field(
        default="development",
        description="Environment (development, production, etc.)"
    )


def load_settings() -> Settings:
    """Load settings with proper error handling."""
    try:
        return Settings()
    except Exception as e:
        error_msg = f"Failed to load settings: {e}"
        if "llm_api_key" in str(e).lower():
            error_msg += "\nMake sure to set LLM_API_KEY in your .env file"
        raise ValueError(error_msg) from e

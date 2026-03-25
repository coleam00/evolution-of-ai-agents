"""Main skill-based agent implementation with progressive disclosure."""

import logging
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from typing import Optional

from src.providers import get_llm_model
from src.dependencies import AgentDependencies
from src.prompts import MAIN_SYSTEM_PROMPT
from src.skill_toolset import skill_tools
from src.http_tools import http_get, http_post
from src.db_tools import save_note, search_notes
from src.settings import load_settings

# Initialize settings
_settings = load_settings()

# Configure Logfire only if token is present
if _settings.logfire_token:
    try:
        import logfire

        logfire.configure(
            token=_settings.logfire_token,
            send_to_logfire='if-token-present',
            service_name=_settings.logfire_service_name,
            environment=_settings.logfire_environment,
            console=logfire.ConsoleOptions(show_project_link=False),
        )

        # Instrument Pydantic AI
        logfire.instrument_pydantic_ai()

        # Instrument HTTP requests to LLM providers
        logfire.instrument_httpx(capture_all=True)

        logger = logging.getLogger(__name__)
        logger.info(f"logfire_enabled: service={_settings.logfire_service_name}")
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"logfire_initialization_failed: {str(e)}")
else:
    logger = logging.getLogger(__name__)
    logger.info("logfire_disabled: token not provided")


class AgentState(BaseModel):
    """Minimal shared state for the skill agent."""

    pass


# Create the skill-based agent
skill_agent = Agent(
    get_llm_model(),
    deps_type=AgentDependencies,
    system_prompt="",  # Will be set dynamically via decorator
    toolsets=[skill_tools],  # Register skill toolset here
)


@skill_agent.system_prompt
async def get_system_prompt(ctx: RunContext[AgentDependencies]) -> str:
    """
    Generate system prompt with skill metadata.

    This dynamically injects skill metadata into the system prompt,
    implementing Level 1 of progressive disclosure.

    Args:
        ctx: Agent runtime context with dependencies

    Returns:
        Complete system prompt with skill metadata injected
    """
    # Initialize dependencies (including skill loader)
    await ctx.deps.initialize()

    # Get skill metadata for prompt
    skill_metadata = ""
    if ctx.deps.skill_loader:
        skill_metadata = ctx.deps.skill_loader.get_skill_metadata_prompt()

    # Inject skill metadata into base prompt
    return MAIN_SYSTEM_PROMPT.format(skill_metadata=skill_metadata)


@skill_agent.tool
async def http_get_tool(
    ctx: RunContext[AgentDependencies],
    url: str,
) -> str:
    """
    Make an HTTP GET request to fetch data from a URL.

    Use this tool when you need to:
    - Fetch data from an API (like weather, stock prices, etc.)
    - Retrieve content from a web page
    - Make any GET request to an external service

    Args:
        ctx: Agent runtime context with dependencies
        url: The full URL to fetch (e.g., "https://api.example.com/data")

    Returns:
        Response body (JSON is formatted nicely), or error message if request fails
    """
    return await http_get(ctx, url)


@skill_agent.tool
async def http_post_tool(
    ctx: RunContext[AgentDependencies],
    url: str,
    body: Optional[str] = None,
) -> str:
    """
    Make an HTTP POST request to send data to a URL.

    Use this tool when you need to:
    - Send data to an API
    - Submit form data
    - Make any POST request to an external service

    Args:
        ctx: Agent runtime context with dependencies
        url: The full URL to post to
        body: Request body as a string (use JSON string for JSON APIs)

    Returns:
        Response body, or error message if request fails
    """
    return await http_post(ctx, url, body)


@skill_agent.tool
async def save_note_tool(
    ctx: RunContext[AgentDependencies],
    title: str,
    content: str,
    source: Optional[str] = None,
    tags: Optional[str] = None,
) -> str:
    """
    Save a note to the persistent Neon Postgres database.

    Use this tool when the user wants to:
    - Save information, findings, or decisions for later
    - Remember something across sessions
    - Store a URL, research result, or any text with a title

    Args:
        ctx: Agent runtime context with dependencies
        title: Short title summarizing what is being saved
        content: Full text content of the note
        source: Optional URL or citation where the information came from
        tags: Optional comma-separated tag string (e.g., "ai,research,tools")

    Returns:
        Confirmation with the new note ID and timestamp, or an error message
    """
    return await save_note(ctx, title, content, source, tags)


@skill_agent.tool
async def search_notes_tool(
    ctx: RunContext[AgentDependencies],
    keyword: str,
) -> str:
    """
    Search previously saved notes by keyword.

    Use this tool when the user wants to:
    - Find notes they saved earlier
    - Retrieve information stored in a previous session
    - Search across all saved notes for a topic

    Args:
        ctx: Agent runtime context with dependencies
        keyword: Search term to match against note titles, content, and tags

    Returns:
        Formatted list of matching notes (up to 20), or a message if none found
    """
    return await search_notes(ctx, keyword)

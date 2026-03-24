"""Skill tools as a reusable FunctionToolset for progressive disclosure."""

from pydantic_ai.toolsets import FunctionToolset
from pydantic_ai import RunContext
from src.dependencies import AgentDependencies
from src.skill_tools import load_skill, read_skill_file, list_skill_files

# Create the skill tools toolset
skill_tools = FunctionToolset()


@skill_tools.tool
async def load_skill_tool(
    ctx: RunContext[AgentDependencies],
    skill_name: str
) -> str:
    """
    Load the full instructions for a skill (Level 2 progressive disclosure).

    Use this tool when you need to access the detailed instructions
    for a skill. Based on the skill descriptions in your system prompt,
    identify which skill is relevant and load its full instructions.

    Args:
        ctx: Agent runtime context with dependencies
        skill_name: Name of the skill to load (e.g., "weather", "code_review")

    Returns:
        Full skill instructions from SKILL.md
    """
    return await load_skill(ctx, skill_name)


@skill_tools.tool
async def read_skill_file_tool(
    ctx: RunContext[AgentDependencies],
    skill_name: str,
    file_path: str
) -> str:
    """
    Read a file from a skill's directory (Level 3 progressive disclosure).

    Use this tool when skill instructions reference a resource file
    (e.g., "See references/api_reference.md for API details").
    This loads the specific resource on-demand.

    Args:
        ctx: Agent runtime context with dependencies
        skill_name: Name of the skill containing the file
        file_path: Relative path to the file (e.g., "references/api_reference.md")

    Returns:
        Contents of the requested file
    """
    return await read_skill_file(ctx, skill_name, file_path)


@skill_tools.tool
async def list_skill_files_tool(
    ctx: RunContext[AgentDependencies],
    skill_name: str,
    directory: str = ""
) -> str:
    """
    List files available in a skill's directory.

    Use this tool to discover what resources are available in a skill
    before loading them. Helpful when you need to explore what
    documentation, scripts, or other files a skill provides.

    Args:
        ctx: Agent runtime context with dependencies
        skill_name: Name of the skill to list files from
        directory: Optional subdirectory to list (e.g., "references", "scripts")

    Returns:
        Formatted list of available files
    """
    return await list_skill_files(ctx, skill_name, directory)

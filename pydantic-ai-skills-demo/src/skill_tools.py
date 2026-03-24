"""Progressive disclosure tools for skill-based agent."""

import logging
from typing import TYPE_CHECKING

from pydantic_ai import RunContext

if TYPE_CHECKING:
    from src.dependencies import AgentDependencies

logger = logging.getLogger(__name__)


async def load_skill(
    ctx: RunContext["AgentDependencies"],
    skill_name: str,
) -> str:
    """
    Load the full instructions for a skill (Level 2 progressive disclosure).

    This tool implements Level 2 of the progressive disclosure pattern.
    When the agent decides a skill is needed based on Level 1 metadata,
    it calls this tool to get the full instructions from SKILL.md.

    Args:
        ctx: Agent runtime context with dependencies
        skill_name: Name of the skill to load

    Returns:
        Full skill instructions from SKILL.md (body only, without frontmatter)
    """
    skill_loader = ctx.deps.skill_loader

    if skill_loader is None:
        logger.error("load_skill_failed: skill_loader not initialized")
        return "Error: Skill loader not initialized. Please try again."

    if skill_name not in skill_loader.skills:
        available = list(skill_loader.skills.keys())
        logger.warning(f"load_skill_not_found: skill_name={skill_name}, available={available}")
        return f"Error: Skill '{skill_name}' not found. Available skills: {available}"

    skill = skill_loader.skills[skill_name]
    skill_md = skill.skill_path / "SKILL.md"

    try:
        content = skill_md.read_text(encoding="utf-8")

        # Strip YAML frontmatter - return only body
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                body = parts[2].strip()
                logger.info(f"load_skill_success: skill_name={skill_name}, body_length={len(body)}")
                return body

        # No frontmatter, return as-is
        logger.info(f"load_skill_success: skill_name={skill_name}, content_length={len(content)}")
        return content

    except Exception as e:
        logger.exception(f"load_skill_error: skill_name={skill_name}, error={str(e)}")
        return f"Error loading skill '{skill_name}': {str(e)}"


async def read_skill_file(
    ctx: RunContext["AgentDependencies"],
    skill_name: str,
    file_path: str,
) -> str:
    """
    Read a file from a skill's directory (Level 3 progressive disclosure).

    This tool implements Level 3 of the progressive disclosure pattern.
    When skill instructions reference a resource file (e.g., "See references/api_docs.md"),
    the agent calls this tool to load that specific resource.

    Security: Validates that the requested file is within the skill directory
    to prevent directory traversal attacks.

    Args:
        ctx: Agent runtime context with dependencies
        skill_name: Name of the skill containing the file
        file_path: Relative path to the file within the skill directory

    Returns:
        Contents of the requested file
    """
    skill_loader = ctx.deps.skill_loader

    if skill_loader is None:
        logger.error("read_skill_file_failed: skill_loader not initialized")
        return "Error: Skill loader not initialized. Please try again."

    if skill_name not in skill_loader.skills:
        available = list(skill_loader.skills.keys())
        logger.warning(
            f"read_skill_file_not_found: skill_name={skill_name}, available={available}"
        )
        return f"Error: Skill '{skill_name}' not found. Available skills: {available}"

    skill = skill_loader.skills[skill_name]
    target_file = skill.skill_path / file_path

    # Security: Ensure file is within skill directory (prevent directory traversal)
    try:
        resolved_target = target_file.resolve()
        resolved_skill = skill.skill_path.resolve()

        if not resolved_target.is_relative_to(resolved_skill):
            logger.warning(
                f"read_skill_file_security_violation: skill_name={skill_name}, "
                f"file_path={file_path}, attempted_path={resolved_target}"
            )
            return f"Error: Access denied - file must be within skill directory"
    except ValueError:
        # is_relative_to raises ValueError on Windows in some cases
        logger.warning(
            f"read_skill_file_path_error: skill_name={skill_name}, file_path={file_path}"
        )
        return f"Error: Invalid file path"

    if not target_file.exists():
        logger.warning(
            f"read_skill_file_not_found: skill_name={skill_name}, file_path={file_path}"
        )
        return f"Error: File not found: {file_path}"

    if not target_file.is_file():
        logger.warning(
            f"read_skill_file_not_a_file: skill_name={skill_name}, file_path={file_path}"
        )
        return f"Error: Path is not a file: {file_path}"

    try:
        content = target_file.read_text(encoding="utf-8")
        logger.info(
            f"read_skill_file_success: skill_name={skill_name}, "
            f"file_path={file_path}, content_length={len(content)}"
        )
        return content

    except Exception as e:
        logger.exception(
            f"read_skill_file_error: skill_name={skill_name}, "
            f"file_path={file_path}, error={str(e)}"
        )
        return f"Error reading file '{file_path}': {str(e)}"


async def list_skill_files(
    ctx: RunContext["AgentDependencies"],
    skill_name: str,
    directory: str = "",
) -> str:
    """
    List files available in a skill's directory.

    This tool helps the agent discover what resources are available
    within a skill before loading them. Useful when the agent needs
    to explore what documentation or scripts are available.

    Args:
        ctx: Agent runtime context with dependencies
        skill_name: Name of the skill to list files from
        directory: Optional subdirectory to list (e.g., "references")

    Returns:
        Formatted list of available files
    """
    skill_loader = ctx.deps.skill_loader

    if skill_loader is None:
        logger.error("list_skill_files_failed: skill_loader not initialized")
        return "Error: Skill loader not initialized. Please try again."

    if skill_name not in skill_loader.skills:
        available = list(skill_loader.skills.keys())
        logger.warning(
            f"list_skill_files_not_found: skill_name={skill_name}, available={available}"
        )
        return f"Error: Skill '{skill_name}' not found. Available skills: {available}"

    skill = skill_loader.skills[skill_name]
    target_dir = skill.skill_path / directory if directory else skill.skill_path

    # Security check for directory parameter
    if directory:
        try:
            resolved_target = target_dir.resolve()
            resolved_skill = skill.skill_path.resolve()

            if not resolved_target.is_relative_to(resolved_skill):
                logger.warning(
                    f"list_skill_files_security_violation: skill_name={skill_name}, "
                    f"directory={directory}"
                )
                return f"Error: Access denied - directory must be within skill directory"
        except ValueError:
            logger.warning(
                f"list_skill_files_path_error: skill_name={skill_name}, directory={directory}"
            )
            return f"Error: Invalid directory path"

    if not target_dir.exists():
        logger.warning(
            f"list_skill_files_dir_not_found: skill_name={skill_name}, directory={directory}"
        )
        return f"Error: Directory not found: {directory or 'skill root'}"

    if not target_dir.is_dir():
        logger.warning(
            f"list_skill_files_not_a_dir: skill_name={skill_name}, directory={directory}"
        )
        return f"Error: Path is not a directory: {directory}"

    try:
        files = []
        for item in target_dir.rglob("*"):
            if item.is_file():
                # Get path relative to skill directory
                rel_path = item.relative_to(skill.skill_path)
                files.append(str(rel_path))

        if not files:
            return f"No files found in skill '{skill_name}'" + (
                f" directory '{directory}'" if directory else ""
            )

        file_list = "\n".join(f"- {f}" for f in sorted(files))
        logger.info(
            f"list_skill_files_success: skill_name={skill_name}, "
            f"directory={directory or 'root'}, file_count={len(files)}"
        )
        return f"Files available in skill '{skill_name}':\n{file_list}"

    except Exception as e:
        logger.exception(
            f"list_skill_files_error: skill_name={skill_name}, "
            f"directory={directory}, error={str(e)}"
        )
        return f"Error listing files: {str(e)}"

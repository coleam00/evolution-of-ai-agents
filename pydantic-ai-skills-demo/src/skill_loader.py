"""Skill loader for discovering and managing skills with progressive disclosure."""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SkillMetadata(BaseModel):
    """Skill metadata from YAML frontmatter."""

    name: str = Field(..., description="Unique skill identifier")
    description: str = Field(..., description="Brief description for agent discovery")
    version: str = Field(default="1.0.0", description="Skill version")
    author: str = Field(default="", description="Skill author")
    skill_path: Path = Field(..., description="Path to skill directory")


class SkillLoader:
    """Loads and manages skills from filesystem."""

    def __init__(self, skills_dir: Path) -> None:
        """
        Initialize the skill loader.

        Args:
            skills_dir: Directory containing skill folders
        """
        self.skills_dir = skills_dir
        self.skills: Dict[str, SkillMetadata] = {}

    def discover_skills(self) -> List[SkillMetadata]:
        """
        Scan skills directory and extract metadata from all SKILL.md files.

        Returns:
            List of discovered skill metadata
        """
        discovered: List[SkillMetadata] = []

        if not self.skills_dir.exists():
            logger.warning(f"skills_directory_missing: path={self.skills_dir}")
            return discovered

        # Scan for skill directories
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue

            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                logger.debug(f"skill_md_missing: dir={skill_dir.name}")
                continue

            # Parse skill metadata
            metadata = self._parse_skill_metadata(skill_md, skill_dir)
            if metadata:
                self.skills[metadata.name] = metadata
                discovered.append(metadata)
                logger.info(f"skill_discovered: name={metadata.name}, version={metadata.version}")

        logger.info(f"skill_discovery_completed: count={len(discovered)}")
        return discovered

    def get_skill_metadata_prompt(self) -> str:
        """
        Generate system prompt section with all skill metadata.

        Returns:
            Formatted string with skill names and descriptions for system prompt
        """
        if not self.skills:
            return "No skills currently available."

        lines: List[str] = []
        for skill in self.skills.values():
            lines.append(f"- **{skill.name}**: {skill.description}")

        return "\n".join(lines)

    def _parse_skill_metadata(
        self, skill_md: Path, skill_dir: Path
    ) -> Optional[SkillMetadata]:
        """
        Extract YAML frontmatter from SKILL.md.

        Args:
            skill_md: Path to SKILL.md file
            skill_dir: Path to skill directory

        Returns:
            SkillMetadata if parsing succeeds, None otherwise
        """
        try:
            content = skill_md.read_text(encoding="utf-8")

            # Check for YAML frontmatter
            if not content.startswith("---"):
                logger.warning(f"skill_missing_frontmatter: file={skill_md}")
                return None

            # Split frontmatter from body
            parts = content.split("---", 2)
            if len(parts) < 3:
                logger.warning(f"skill_invalid_frontmatter: file={skill_md}")
                return None

            # Parse YAML frontmatter
            frontmatter_yaml = parts[1].strip()
            frontmatter = yaml.safe_load(frontmatter_yaml)

            if not frontmatter:
                logger.warning(f"skill_empty_frontmatter: file={skill_md}")
                return None

            # Validate required fields
            if "name" not in frontmatter or "description" not in frontmatter:
                logger.warning(
                    f"skill_missing_required_fields: file={skill_md}, "
                    f"has_name={'name' in frontmatter}, has_description={'description' in frontmatter}"
                )
                return None

            # Create metadata with skill_path
            return SkillMetadata(
                name=frontmatter["name"],
                description=frontmatter["description"],
                version=frontmatter.get("version", "1.0.0"),
                author=frontmatter.get("author", ""),
                skill_path=skill_dir,
            )

        except yaml.YAMLError as e:
            logger.error(f"skill_yaml_parse_error: file={skill_md}, error={str(e)}")
            return None
        except Exception as e:
            logger.exception(f"skill_parse_error: file={skill_md}, error={str(e)}")
            return None

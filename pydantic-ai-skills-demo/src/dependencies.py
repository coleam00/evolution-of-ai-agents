"""Dependencies for Skill-Based Agent."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import logging
from pathlib import Path

from src.skill_loader import SkillLoader
from src.settings import load_settings

logger = logging.getLogger(__name__)


@dataclass
class AgentDependencies:
    """Dependencies injected into the agent context."""

    # Skill system
    skill_loader: Optional[SkillLoader] = None

    # Session context
    session_id: Optional[str] = None
    user_preferences: Dict[str, Any] = field(default_factory=dict)

    # Configuration
    settings: Optional[Any] = None

    async def initialize(self) -> None:
        """
        Initialize skill loader and settings.

        Raises:
            ValueError: If settings cannot be loaded
        """
        if not self.settings:
            self.settings = load_settings()
            logger.info(f"settings_loaded: skills_dir={self.settings.skills_dir}")

        if not self.skill_loader:
            skills_dir = Path(self.settings.skills_dir)
            self.skill_loader = SkillLoader(skills_dir)
            skills = self.skill_loader.discover_skills()

            logger.info(f"skill_loader_initialized: skills_count={len(skills)}")

            # Log discovered skills
            for skill in skills:
                logger.debug(f"skill_available: name={skill.name}, description={skill.description}")

    def set_user_preference(self, key: str, value: Any) -> None:
        """
        Set a user preference for the session.

        Args:
            key: Preference key
            value: Preference value
        """
        self.user_preferences[key] = value

    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a user preference.

        Args:
            key: Preference key
            default: Default value if key not found

        Returns:
            Preference value or default
        """
        return self.user_preferences.get(key, default)

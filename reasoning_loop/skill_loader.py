"""
Skill Loader for Silver Tier AI Employee.

Dynamically loads agent skills from Skills folder based on task requirements.
"""
from pathlib import Path
from typing import Dict, Any, Optional, List
import frontmatter
import sys
sys.path.append(str(Path(__file__).parent.parent))

from shared.folder_paths import SKILLS
from shared.logging_config import get_logger

logger = get_logger(__name__)


class SkillLoader:
    """
    Loads and manages agent skills from the Skills folder.

    Skills are stored as Markdown files with YAML frontmatter.
    """

    def __init__(self):
        """Initialize skill loader."""
        self.skills: Dict[str, Dict[str, Any]] = {}
        self.load_all_skills()

    def load_all_skills(self):
        """Load all skills from the Skills folder."""
        if not SKILLS.exists():
            logger.warning(f"Skills folder not found: {SKILLS}")
            return

        skill_files = list(SKILLS.glob("*.md"))
        logger.info(f"Loading {len(skill_files)} skills from {SKILLS}")

        for skill_file in skill_files:
            try:
                skill_data = self.load_skill(skill_file)
                skill_name = skill_data['metadata']['skill_name']
                self.skills[skill_name] = skill_data
                logger.debug(f"Loaded skill: {skill_name}")
            except Exception as e:
                logger.error(f"Error loading skill {skill_file.name}: {e}", exc_info=True)

        logger.info(f"Successfully loaded {len(self.skills)} skills")

    def load_skill(self, skill_file: Path) -> Dict[str, Any]:
        """
        Load a single skill file.

        Args:
            skill_file: Path to skill file

        Returns:
            Dictionary with 'metadata' and 'content' keys

        Raises:
            FileNotFoundError: If skill file doesn't exist
            ValueError: If skill format is invalid
        """
        if not skill_file.exists():
            raise FileNotFoundError(f"Skill file not found: {skill_file}")

        with open(skill_file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        # Validate required fields
        required_fields = ['skill_name', 'description', 'version', 'required_permissions', 'requires_approval']
        metadata = dict(post.metadata)

        for field in required_fields:
            if field not in metadata:
                raise ValueError(f"Skill {skill_file.name} missing required field: {field}")

        return {
            'metadata': metadata,
            'content': post.content,
            'file_path': skill_file
        }

    def get_skill(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a skill by name.

        Args:
            skill_name: Name of the skill to retrieve

        Returns:
            Skill data dictionary, or None if not found
        """
        return self.skills.get(skill_name)

    def get_skill_by_permission(self, permission: str) -> List[Dict[str, Any]]:
        """
        Get all skills that have a specific permission.

        Args:
            permission: Permission to search for (e.g., 'mcp_email')

        Returns:
            List of skill data dictionaries
        """
        matching_skills = []
        for skill_data in self.skills.values():
            permissions = skill_data['metadata'].get('required_permissions', [])
            if permission in permissions:
                matching_skills.append(skill_data)
        return matching_skills

    def requires_approval(self, skill_name: str) -> bool:
        """
        Check if a skill requires human approval.

        Args:
            skill_name: Name of the skill

        Returns:
            True if skill requires approval, False otherwise
        """
        skill = self.get_skill(skill_name)
        if not skill:
            logger.warning(f"Skill not found: {skill_name}")
            return True  # Default to requiring approval for safety

        return skill['metadata'].get('requires_approval', False)

    def get_skill_content(self, skill_name: str) -> Optional[str]:
        """
        Get the execution logic content for a skill.

        Args:
            skill_name: Name of the skill

        Returns:
            Skill content (markdown), or None if not found
        """
        skill = self.get_skill(skill_name)
        if not skill:
            return None
        return skill['content']

    def list_skills(self) -> List[str]:
        """
        Get list of all loaded skill names.

        Returns:
            List of skill names
        """
        return list(self.skills.keys())

    def reload_skills(self):
        """Reload all skills from disk."""
        self.skills.clear()
        self.load_all_skills()


if __name__ == "__main__":
    # Test skill loader
    loader = SkillLoader()

    print(f"Loaded skills: {loader.list_skills()}")

    # Test getting a specific skill
    planner = loader.get_skill("planner_skill")
    if planner:
        print(f"\nPlanner skill:")
        print(f"  Description: {planner['metadata']['description']}")
        print(f"  Version: {planner['metadata']['version']}")
        print(f"  Requires approval: {planner['metadata']['requires_approval']}")
        print(f"  Permissions: {planner['metadata']['required_permissions']}")

    # Test permission search
    email_skills = loader.get_skill_by_permission("mcp_email")
    print(f"\nSkills with mcp_email permission: {[s['metadata']['skill_name'] for s in email_skills]}")

    # Test approval check
    print(f"\nPlanner requires approval: {loader.requires_approval('planner_skill')}")

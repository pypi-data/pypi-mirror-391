"""Server state management for MCP Skill Server."""

import os
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass, field

from .skill_loader import Skill


@dataclass
class ServerState:
    """
    Manages the runtime state of the MCP Skill Server.

    This includes:
    - Skills directory path (can be set dynamically)
    - Loaded skills cache
    - Client capability flags
    - Environment variables
    """

    # Skills directory (can be None initially, set later via tool)
    skills_directory: Optional[Path] = None

    # Currently loaded skills
    current_skills: Dict[str, Skill] = field(default_factory=dict)

    # Client capabilities detected during initialization
    supports_list_changed: bool = False

    # Environment variable override
    env_skills_dir: Optional[str] = field(default=None)

    # Command-line argument override
    cli_skills_dir: Optional[Path] = None

    def __post_init__(self):
        """Initialize environment variable."""
        self.env_skills_dir = os.getenv('MCP_SKILLS_DIR')

    def get_effective_skills_directory(self) -> Optional[Path]:
        """
        Get the effective skills directory based on priority order.

        Priority (highest to lowest):
        1. Command-line argument (--skills-dir)
        2. Environment variable (MCP_SKILLS_DIR)
        3. Dynamically set path (via set_skills_directory tool)
        4. Project-level discovery (.claude/skills/ or .skill in project root)
        5. Global fallback (~/.skill)

        Returns:
            Path to skills directory or None if not found
        """
        # Priority 1: CLI argument
        if self.cli_skills_dir is not None:
            if self.cli_skills_dir.exists():
                return self.cli_skills_dir

        # Priority 2: Environment variable
        if self.env_skills_dir:
            env_path = Path(self.env_skills_dir)
            if env_path.exists():
                return env_path

        # Priority 3: Dynamically set directory
        if self.skills_directory is not None:
            if self.skills_directory.exists():
                return self.skills_directory

        # Priority 4: Project-level discovery
        project_skill_dir = self._find_project_skill_dir()
        if project_skill_dir is not None:
            return project_skill_dir

        # Priority 5: Global fallback
        global_skill_dir = Path.home() / ".skill"
        if global_skill_dir.exists():
            return global_skill_dir

        return None

    def _find_project_skill_dir(self) -> Optional[Path]:
        """
        Find project-level skills directory by traversing up from current directory.

        Looks for project root markers:
        - .git/
        - .claude/
        - .skill/
        - package.json
        - pyproject.toml, setup.py
        - Cargo.toml
        - go.mod

        Supports both ClaudeCode format (.claude/skills/) and legacy format (.skill/)

        Returns:
            Path to skills directory in project root, or None if not found
        """
        current = Path.cwd()

        # Traverse up the directory tree
        while current != current.parent:
            # Check if this is a project root
            is_project_root = any([
                (current / ".git").is_dir(),
                (current / ".claude").is_dir(),
                (current / ".skill").is_dir(),
                (current / "package.json").is_file(),
                (current / "pyproject.toml").is_file(),
                (current / "setup.py").is_file(),
                (current / "Cargo.toml").is_file(),
                (current / "go.mod").is_file(),
            ])

            if is_project_root:
                # Priority 1: ClaudeCode format (.claude/skills/)
                claude_skill_dir = current / ".claude" / "skills"
                if claude_skill_dir.is_dir():
                    return claude_skill_dir

                # Priority 2: Legacy format (.skill/)
                skill_dir = current / ".skill"
                if skill_dir.is_dir():
                    return skill_dir

            current = current.parent

        return None

    def set_skills_directory(self, path: str) -> tuple[bool, str]:
        """
        Set the skills directory dynamically.

        Args:
            path: Absolute or relative path to skills directory

        Returns:
            Tuple of (success: bool, message: str)
        """
        skills_path = Path(path).resolve()

        # Validate path exists
        if not skills_path.exists():
            return False, f"Path does not exist: {skills_path}"

        # Validate it's a directory
        if not skills_path.is_dir():
            return False, f"Path is not a directory: {skills_path}"

        # Check for skills subdirectories if path doesn't already point to one
        if skills_path.name not in [".skill", "skills"]:
            # Priority 1: Check for .claude/skills/ (ClaudeCode format)
            claude_skill_dir = skills_path / ".claude" / "skills"
            if claude_skill_dir.is_dir():
                skills_path = claude_skill_dir
            else:
                # Priority 2: Check for .skill/ (legacy format)
                potential_skill_dir = skills_path / ".skill"
                if potential_skill_dir.is_dir():
                    skills_path = potential_skill_dir

        self.skills_directory = skills_path
        return True, f"Skills directory set to: {skills_path}"

    def update_skills(self, skills: Dict[str, Skill]):
        """Update the current skills cache."""
        self.current_skills = skills

    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a skill by name from cache."""
        return self.current_skills.get(name)

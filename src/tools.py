from pathlib import Path
from typing import Any

import yaml
from langchain.tools import tool

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"


def _extract_frontmatter(content: str) -> dict[str, Any]:
    """Extract YAML frontmatter from a markdown string.

    Args:
        content: Full markdown document content.

    Returns:
        Parsed frontmatter as a dictionary, or an empty dictionary when no
        valid frontmatter is present.
    """
    if content.startswith("---"):
        end_idx = content.find("---", 3)
        if end_idx != -1:
            frontmatter = content[3:end_idx].strip()
            try:
                return yaml.safe_load(frontmatter) or {}
            except yaml.YAMLError:
                return {}
    return {}


def _resolve_skill_path(skill_name: str) -> Path:
    """Resolve the directory path for a named skill.

    Args:
        skill_name: Skill directory name under `skills/`.

    Returns:
        Absolute path to the requested skill directory.
    """
    return SKILLS_DIR / skill_name


@tool
def progressive_skill_loader(skill_name: str, load_type: str, linked_path: str | None = None) -> dict[str, Any] | str:
    """
    Tool for progressively loading a skill from the skills directory.

    This tool supports loading the YAML frontmatter separately, the entire skill content,
    or traversing to and loading files linked in the skill (e.g., 'references/EXAMPLES.md').

    The skill is assumed to be a directory under 'skills/' with a main 'SKILL.md' file
    containing YAML frontmatter. Linked paths are relative to the skill directory.

    Args:
        skill_name (str): The name of the skill (subdirectory under 'skills/').
        load_type (str): One of 'frontmatter' (returns dict), 'full' (returns str of entire content),
                        or 'linked' (returns str of linked file content).
        linked_path (str, optional): Relative path to the linked file for 'linked' load_type.

    Returns:
        dict for 'frontmatter', str for 'full' or 'linked'.

    Raises:
        ValueError: If invalid load_type or missing linked_path for 'linked'.
        FileNotFoundError: If the file does not exist.
    """
    base_dir = _resolve_skill_path(skill_name)
    main_file = base_dir / "SKILL.md"

    if load_type == "frontmatter":
        return _extract_frontmatter(main_file.read_text(encoding="utf-8"))

    if load_type == "full":
        return main_file.read_text(encoding="utf-8")

    if load_type == "linked":
        if not linked_path:
            raise ValueError("linked_path is required for 'linked' load_type")
        linked_file = (base_dir / linked_path).resolve()
        if base_dir.resolve() not in linked_file.parents and linked_file != base_dir.resolve():
            raise ValueError("linked_path must stay inside the skill directory")
        return linked_file.read_text(encoding="utf-8")

    raise ValueError("load_type must be one of 'frontmatter', 'full', or 'linked'")
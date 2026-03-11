import os
from langchain.tools import tool
import yaml


@tool
def progressive_skill_loader(skill_name: str, load_type: str, linked_path: str = None) -> dict | str:
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
    base_dir = os.path.join('skills', skill_name)
    main_file = os.path.join(base_dir, 'SKILL.md')

    def extract_frontmatter(content: str) -> dict:
        if content.startswith('---'):
            end_idx = content.find('---', 3)
            if end_idx != -1:
                fm_str = content[3:end_idx].strip()
                try:
                    return yaml.safe_load(fm_str)
                except yaml.YAMLError:
                    return {}
        return {}

    if load_type == 'frontmatter':
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return extract_frontmatter(content)

    elif load_type == 'full':
        with open(main_file, 'r', encoding='utf-8') as f:
            return f.read()

    elif load_type == 'linked':
        if not linked_path:
            raise ValueError("linked_path is required for 'linked' load_type")
        linked_file = os.path.join(base_dir, linked_path)
        with open(linked_file, 'r', encoding='utf-8') as f:
            return f.read()

    else:
        raise ValueError("load_type must be one of 'frontmatter', 'full', or 'linked'")
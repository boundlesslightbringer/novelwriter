from src.tools import _resolve_skill_path
from src.tools import progressive_skill_loader


def test_resolve_skill_path_supports_character_integration_alias() -> None:
    path = _resolve_skill_path("character-integration")
    assert path.name == "character-integration-with-plot"
    assert path.joinpath("SKILL.md").exists()


def test_resolve_skill_path_supports_underscore_alias_variant() -> None:
    path = _resolve_skill_path("character_integration")
    assert path.name == "character-integration-with-plot"
    assert path.joinpath("SKILL.md").exists()


def test_progressive_skill_loader_accepts_content_alias_for_full() -> None:
    content = progressive_skill_loader.invoke({"skill_name": "finding-a-seed", "load_type": "content"})
    assert isinstance(content, str)
    assert len(content) > 0

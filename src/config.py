from typing import Dict, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseModel):
    """Configuration for an LLM model."""
    model_name: str = Field(default="gemini-3-flash-preview")
    model_provider: str = Field(default="google_genai")
    temperature: float = Field(default=0.5)
    top_p: Optional[float] = Field(default=0.95)
    top_k: Optional[int] = Field(default=None)
    seed: Optional[int] = Field(default=None)


class NovelWriterConfig(BaseSettings):
    """Global configuration for the GRRM Novel Writer."""
    
    # Global LLM settings (used as default)
    default_llm: LLMConfig = Field(default_factory=LLMConfig)
    
    # Per-agent overrides (e.g., {"writing_subagent": LLMConfig(temperature=0.9)})
    agent_llm_overrides: Dict[str, LLMConfig] = {
    "brain": LLMConfig(model_name="gemini-3-flash-preview", temperature=0)
}
    
    # Orchestrator settings
    max_brain_iterations: int = Field(default=15)
    max_rejection_budget: int = Field(default=2)
    mvp_default_chapter_context: int = Field(default=1)
    mvp_max_major_characters: int = Field(default=5)
    mvp_target_scene_pages: str = Field(default="1-2")
    
    # MongoDB settings
    mongodb_uri: str = Field(default="mongodb://localhost:27017/")
    mongodb_db_name: str = Field(default="novelwriter_kg")
    mongodb_checkpoint_db_name: str = Field(default="novelwriter_checkpoints")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    def get_llm_config(self, agent_name: Optional[str] = None) -> LLMConfig:
        """Get the LLM configuration for a specific agent, falling back to default."""
        if agent_name and agent_name in self.agent_llm_overrides:
            return self.agent_llm_overrides[agent_name]
        return self.default_llm

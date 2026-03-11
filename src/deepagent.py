"""
GRRM Novel Writer - DeepAgent Brain

The central orchestrator of the George R.R. Martin-inspired novel-writing system.
Generates one chapter per session through structured workflow of skill-group subagent delegation.
"""

from deepagents import create_deep_agent
from langchain.tools import tool 
import os
import markdown
from langchain.tools import tool
import os
import yaml
from tools import progressive_skill_loader
from world_bible_tools import (
    read_world_bible_current_state,
    read_world_bible_excerpt,
    append_world_bible_update,
    create_world_bible_snapshot,
    query_world_bible,
    detect_world_bible_contradiction,
    get_world_bible_changelog,
    get_world_bible_at_chapter,
    initialize_world_bible
)

with open("src/subagent_prompts/planning_subagent.md", "r", encoding="utf-8") as f:
   PLANNING_SUBAGENT_SYSTEM_PROMPT = markdown.markdown(f.read())

with open("src/orchestrator_prompt.md", "r", encoding="utf-8") as f:
   ORCHESTRATOR_SYSTEM_PROMPT = markdown.markdown(f.read())

# Planning Subagent - Group 1 skills
planning_subagent = {
   "name": "planning_subagent",
   "description": "The Planning Subagent is responsible for all Group 1 – Planning skills: finding-a-seed, defining-rough-endpoints, worldbuilding, research-integration. It is responsible for establishing the story's foundation: from initial seed through world construction.",
   "model": "anthropic:claude-sonnet-4-20250514",
   "tools": [progressive_skill_loader],
   "system_prompt": PLANNING_SUBAGENT_SYSTEM_PROMPT
}

# World Bible Manager Subagent - Infrastructure for ALL World Bible operations
worldbible_manager = {
   "name": "worldbible_manager",
   "description": "The World Bible Manager handles ALL World Bible read/write operations. It maintains the sole ground truth for story state using a JSONL append-only format. Other agents never access the World Bible directly - they delegate to this subagent.",
   "model": "anthropic:claude-sonnet-4-20250514",
   "tools": [
       read_world_bible_current_state,
       read_world_bible_excerpt,
       append_world_bible_update,
       create_world_bible_snapshot,
       query_world_bible,
       detect_world_bible_contradiction,
       get_world_bible_changelog,
       get_world_bible_at_chapter,
       initialize_world_bible
   ],
   "system_prompt": """You are the World Bible Manager - the sole gatekeeper of story state.

Your responsibilities:
1. Handle ALL World Bible read/write operations via the JSONL filesystem backend
2. Maintain append-only changelog integrity
3. Detect and flag contradictions before writes are committed
4. Create snapshots at chapter boundaries
5. Never allow direct World Bible access to other agents - all queries go through you

When receiving a request:
- For reads: Use query_world_bible or read_world_bible_excerpt to fetch data
- For writes: First run detect_world_bible_contradiction, then append_world_bible_update
- For chapter completion: Always create_world_bible_snapshot
- For excerpts to subagents: Use read_world_bible_excerpt with appropriate filters

Return structured output with the requested data and confirmation of any writes."""
}

# Orchestrator agent with World Bible tools for direct orchestration
orchestrator = create_deep_agent(
   name = "orchestrator",
   model = "anthropic:claude-sonnet-4-20250514",
   tools = [
       progressive_skill_loader,
       read_world_bible_current_state,
       read_world_bible_excerpt,
       append_world_bible_update,
       create_world_bible_snapshot,
       query_world_bible,
       detect_world_bible_contradiction,
       get_world_bible_changelog,
       get_world_bible_at_chapter,
       initialize_world_bible
   ],
   subagents = [planning_subagent, worldbible_manager],
   system_prompt = ORCHESTRATOR_SYSTEM_PROMPT
)



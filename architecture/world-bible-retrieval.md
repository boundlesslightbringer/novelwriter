# World Bible Retrieval Patterns

## Overview

This document defines the query patterns and retrieval interface for the World Bible NoSQL storage. It focuses on **working set filtering** - loading only the data necessary for the current scene/chapter, rather than entire modules.

---

## Core Retrieval Philosophy

**Principle:** Never load full modules. Always query for specific working sets.

**Benefits:**
- Reduces per-query data volume by 60-80%
- Faster query execution (<50ms with indexes)
- Less context consumed in agent prompts
- Enables larger novel projects without linear context growth

---

## Query Interface

### Python SDK Pattern

```python
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

@dataclass
class WorkingSetQuery:
    """Defines a working set query for World Bible data"""
    collection: str
    filters: Dict[str, Any]
    fields: List[str]
    sort: Optional[Dict[str, int]] = None
    limit: Optional[int] = None

class WorldBibleInterface:
    """Primary interface for World Bible data retrieval"""
    
    def __init__(self, mongo_client, novel_id: str):
        self.db = mongo_client[f"world_bible_{novel_id}"]
        self.cache = {}  # LRU cache for hot data
    
    def get_working_set(self, query: WorkingSetQuery) -> List[Dict]:
        """Execute a working set query"""
        collection = self.db[query.collection]
        
        # Build projection
        projection = {field: 1 for field in query.fields}
        projection["_id"] = 1  # Always include _id
        
        # Execute query
        cursor = collection.find(query.filters, projection)
        
        if query.sort:
            cursor = cursor.sort(list(query.sort.items()))
        if query.limit:
            cursor = cursor.limit(query.limit)
        
        return list(cursor)
    
    def get_character_state(self, character_id: str, chapter: int) -> Dict:
        """Get character state as of specific chapter"""
        # Query character directory
        character = self.db.character_directory.find_one(
            {"character_id": character_id},
            {
                "character_id": 1,
                "full_name": 1,
                "current_location": 1,
                "emotional_state": 1,
                "active_desires": 1,
                "active_fears": 1,
                "physical_state": 1,
                "arc_type": 1,
                "arc_stage": 1
            }
        )
        
        if not character:
            raise ValueError(f"Character {character_id} not found")
        
        # Get knowledge state as of chapter
        knowledge = self.db.character_knowledge_matrix.find(
            {
                "character_id": character_id,
                "acquired_at_chapter": {"$lte": chapter}
            },
            {
                "information_item_id": 1,
                "status": 1,
                "acquired_at_chapter": 1,
                "dramatic_irony_flag": 1
            }
        ).sort("acquired_at_chapter", -1)
        
        return {
            "character": character,
            "knowledge": list(knowledge)
        }
```

---

## Working Set Query Patterns by Use Case

### 1. Scene Generation - Gardener Plotting System

**Required Data:**
- POV character current state (Module 1.1, 1.2)
- Active plot threads involving POV character (Module 2.3)
- Active consequences affecting POV character (Module 4.1, 4.2)
- Pending payoffs (Module 2.4)

**Query Pattern:**

```python
# Gardener Plotting System Working Set
def get_gardener_working_set(
    pov_character: str,
    current_chapter: int,
    last_scene_outcome: str
) -> Dict:
    
    queries = {
        # 1. POV Character State
        "pov_state": WorkingSetQuery(
            collection="character_directory",
            filters={"character_id": pov_character},
            fields=[
                "character_id", "full_name", "current_location",
                "emotional_state", "active_desires", "active_fears",
                "physical_state", "arc_stage", "last_pov_chapter"
            ]
        ),
        
        # 2. POV Knowledge Matrix (as of current chapter)
        "pov_knowledge": WorkingSetQuery(
            collection="character_knowledge_matrix",
            filters={
                "character_id": pov_character,
                "acquired_at_chapter": {"$lte": current_chapter}
            },
            fields=["information_item_id", "status", "source", "dramatic_irony_flag"],
            sort={"acquired_at_chapter": -1}
        ),
        
        # 3. Active Plot Threads for POV
        "active_threads": WorkingSetQuery(
            collection="plot_thread_registry",
            filters={
                "characters_involved": pov_character,
                "status": "Active"
            },
            fields=[
                "thread_id", "thread_name", "expected_convergence",
                "originating_chapter"
            ]
        ),
        
        # 4. Active Consequences for POV
        "active_consequences": WorkingSetQuery(
            collection="consequence_chains",
            filters={
                "affected_characters": pov_character,
                "$or": [
                    {"consequences.immediate.chapter_played_out": {"$gte": current_chapter - 3}},
                    {"consequences.short_term.chapter_window.start": {"$lte": current_chapter + 2}}
                ]
            },
            fields=[
                "event_id", "triggering_event", "consequences.short_term",
                "consequences.immediate"
            ]
        ),
        
        # 5. Armed Consequence Bombs approaching detonation
        "approaching_bombs": WorkingSetQuery(
            collection="consequence_bombs",
            filters={
                "status": "Armed",
                "estimated_detonation_window.start": {"$lte": current_chapter + 3},
                "estimated_detonation_window.end": {"$gte": current_chapter - 1}
            },
            fields=["bomb_id", "nature_of_future_consequence", "estimated_detonation_window"]
        ),
        
        # 6. Pending Payoffs in current window
        "pending_payoffs": WorkingSetQuery(
            collection="pending_payoffs",
            filters={
                "resolution_status": "Pending",
                "expected_payoff_window.start": {"$lte": current_chapter},
                "expected_payoff_window.end": {"$gte": current_chapter}
            },
            fields=["setup_element", "type", "planted_in_chapter"]
        )
    }
    
    return {name: interface.get_working_set(q) for name, q in queries.items()}
```

**Typical Data Volume:**
- POV state: ~500 bytes
- Knowledge matrix: 20-50 items, ~2KB
- Active threads: 3-8 items, ~1KB
- Active consequences: 2-6 items, ~1.5KB
- Approaching bombs: 0-3 items, ~500 bytes
- Pending payoffs: 1-4 items, ~800 bytes

**Total per scene: ~6-8KB** (vs 50-100KB for full modules)

---

### 2. Scene Construction - Drafting Working Set

**Required Data:**
- POV voice profile (if different from character state)
- World state relevant to scene location (Module 3.x)
- Character relationships with scene participants (Module 1.3)

**Query Pattern:**

```python
# Scene Construction Working Set
def get_scene_construction_working_set(
    pov_character: str,
    scene_participants: List[str],
    location: str,
    current_chapter: int
) -> Dict:
    
    queries = {
        # 1. POV Character Full Profile
        "pov_profile": WorkingSetQuery(
            collection="character_directory",
            filters={"character_id": pov_character},
            fields=[
                "full_name", "physical_description", "social_class",
                "current_location", "emotional_state", "active_desires",
                "active_fears", "pov_chapter_count"
            ]
        ),
        
        # 2. Relationships with participants
        "relationships": WorkingSetQuery(
            collection="relationship_records",
            filters={
                "from_character": pov_character,
                "to_character": {"$in": scene_participants}
            },
            fields=[
                "to_character", "emotional_valence", "power_dynamic",
                "relationship_history", "secrets_kept"
            ]
        ),
        
        # 3. Location details
        "location": WorkingSetQuery(
            collection="geography",
            filters={"location_id": location},
            fields=[
                "location_name", "physical_description",
                "climate.current_weather"
            ]
        ),
        
        # 4. Political context of location
        "political_context": WorkingSetQuery(
            collection="political_power_map",
            filters={
                "territory_id": location,
                "chapter_snapshot": {"$lte": current_chapter}
            },
            fields=["current_controller", "allegiances", "active_enmities"],
            sort={"chapter_snapshot": -1},
            limit=1  # Most recent
        ),
        
        # 5. Local culture (if location has culture data)
        "culture": WorkingSetQuery(
            collection="cultures_customs_religion",
            filters={"region": location},
            fields=["core_values", "core_fears", "customs", "religious_beliefs"]
        )
    }
    
    return {name: interface.get_working_set(q) for name, q in queries.items()}
```

---

### 3. POV Consistency Check - Audit Working Set

**Required Data:**
- POV voice profile (vocabulary, sentence patterns)
- POV knowledge matrix (strict validation)
- Other characters' knowledge states (for head-hopping detection)

**Query Pattern:**

```python
# POV Consistency Working Set
def get_pov_consistency_working_set(
    pov_character: str,
    scene_participants: List[str],
    current_chapter: int
) -> Dict:
    
    queries = {
        # 1. POV Knowledge (strict - only what they know at this chapter)
        "pov_knowledge": WorkingSetQuery(
            collection="character_knowledge_matrix",
            filters={
                "character_id": pov_character,
                "acquired_at_chapter": {"$lte": current_chapter},
                "status": {"$in": ["KNOWS", "SUSPECTS", "BELIEVES"]}
            },
            fields=["information_item_id", "status", "confidence_level"]
        ),
        
        # 2. Other participants' knowledge (for contradiction detection)
        "others_knowledge": WorkingSetQuery(
            collection="character_knowledge_matrix",
            filters={
                "character_id": {"$in": scene_participants},
                "character_id": {"$ne": pov_character},
                "status": "KNOWS",
                "acquired_at_chapter": {"$lte": current_chapter}
            },
            fields=["character_id", "information_item_id", "status"]
        ),
        
        # 3. POV Voice Profile (from Character Voice Differentiation output)
        "voice_profile": WorkingSetQuery(
            collection="character_directory",
            filters={
                "character_id": pov_character,
                "is_pov_character": True
            },
            fields=[
                # Fields that would be populated by Character Voice Differentiation
                "voice_vocabulary_range",
                "voice_sentence_patterns",
                "voice_observational_focus"
            ]
        )
    }
    
    return {name: interface.get_working_set(q) for name, q in queries.items()}
```

---

### 4. Character Integration with Plot - Update Working Set

**Required Data:**
- Full character records for integration
- Relationship records between characters
- Current world state for faction alignment

**Query Pattern:**

```python
# Character Integration Working Set
def get_character_integration_working_set(
    character_ids: List[str],
    current_chapter: int
) -> Dict:
    
    queries = {
        # 1. Full Character Records
        "characters": WorkingSetQuery(
            collection="character_directory",
            filters={"character_id": {"$in": character_ids}},
            fields=[
                "character_id", "full_name", "arc_type", "arc_stage",
                "active_desires", "active_fears", "current_beliefs",
                "core_contradiction"  # If stored
            ]
        ),
        
        # 2. All Relationships between these characters
        "relationships": WorkingSetQuery(
            collection="relationship_records",
            filters={
                "$or": [
                    {"from_character": {"$in": character_ids}, "to_character": {"$in": character_ids}},
                    {"from_character": {"$in": character_ids}},
                    {"to_character": {"$in": character_ids}}
                ]
            },
            fields=[
                "from_character", "to_character", "emotional_valence",
                "power_dynamic", "relationship_history", "secrets_kept"
            ]
        ),
        
        # 3. Current Political State
        "political_state": WorkingSetQuery(
            collection="political_power_map",
            filters={"chapter_snapshot": current_chapter},
            fields=["territory_id", "current_controller", "allegiances"]
        )
    }
    
    return {name: interface.get_working_set(q) for name, q in queries.items()}
```

---

### 5. Consequence Cascade Implementation - Ledger Update

**Required Data:**
- Consequence chains for affected characters
- Existing consequence bombs
- Character relationship network

**Query Pattern:**

```python
# Consequence Cascade Working Set
def get_consequence_cascade_working_set(
    triggering_event: str,
    chapter: int,
    affected_characters: List[str]
) -> Dict:
    
    queries = {
        # 1. Existing consequences for these characters
        "existing_consequences": WorkingSetQuery(
            collection="consequence_chains",
            filters={
                "affected_characters": {"$in": affected_characters},
                "chapter_reference": {"$gte": chapter - 5}  # Recent only
            },
            fields=[
                "event_id", "consequences.short_term",
                "consequences.long_term", "cascade_chain_id"
            ]
        ),
        
        # 2. Active consequence bombs for these characters
        "active_bombs": WorkingSetQuery(
            collection="consequence_bombs",
            filters={
                "status": "Armed",
                "bomb_id": {"$regex": f"^({'|'.join(affected_characters)})"}
            },
            fields=["bomb_id", "nature_of_future_consequence", "trigger_conditions"]
        ),
        
        # 3. Character relationships (for ripple effects)
        "relationships": WorkingSetQuery(
            collection="relationship_records",
            filters={
                "$or": [
                    {"from_character": {"$in": affected_characters}},
                    {"to_character": {"$in": affected_characters}}
                ]
            },
            fields=["from_character", "to_character", "trajectory", "secrets_kept"]
        ),
        
        # 4. Active cascade chains
        "cascade_chains": WorkingSetQuery(
            collection="cascade_chains",
            filters={
                "characters_involved": {"$in": affected_characters},
                "current_position": {"$lt": 5}  # Not too far along
            },
            fields=["chain_id", "chain_sequence", "remaining_links"]
        )
    }
    
    return {name: interface.get_working_set(q) for name, q in queries.items()}
```

---

### 6. Braided Narrative Technique - Convergence Analysis

**Required Data:**
- Multiple POV chapter logs
- Plot thread registry for convergence points
- Timeline for synchronization

**Query Pattern:**

```python
# Braided Narrative Working Set
def get_braided_narrative_working_set(
    pov_characters: List[str],
    current_chapter: int,
    lookback_chapters: int = 5
) -> Dict:
    
    start_chapter = max(1, current_chapter - lookback_chapters)
    
    queries = {
        # 1. Recent chapters from all POVs
        "recent_chapters": WorkingSetQuery(
            collection="pov_chapter_log",
            filters={
                "chapter_number": {"$gte": start_chapter, "$lte": current_chapter}
            },
            fields=[
                "chapter_number", "pov_character", "scenes", "connections",
                "chapter_delta"
            ],
            sort={"chapter_number": -1}
        ),
        
        # 2. Plot threads involving multiple POVs
        "shared_threads": WorkingSetQuery(
            collection="plot_thread_registry",
            filters={
                "characters_involved": {"$in": pov_characters},
                "status": "Active"
            },
            fields=[
                "thread_id", "characters_involved",
                "expected_convergence", "thread_log"
            ]
        ),
        
        # 3. Timeline entries for synchronization
        "timeline_sync": WorkingSetQuery(
            collection="absolute_timeline",
            filters={
                "chapter_snapshot": {"$gte": start_chapter, "$lte": current_chapter}
            },
            fields=["day_number", "simultaneous_events", "chapter_snapshot"]
        )
    }
    
    return {name: interface.get_working_set(q) for name, q in queries.items()}
```

---

## Delta Query Patterns

For efficiency, also support delta queries ("what changed since chapter N"):

```python
# Delta Query - Character State Changes
def get_character_delta(
    character_id: str,
    since_chapter: int,
    to_chapter: int
) -> Dict:
    """Get all changes to a character between two chapters"""
    
    # Use a hypothetical change_log collection (populated on updates)
    # Or query current state and compare
    
    return WorkingSetQuery(
        collection="character_state_changes",
        filters={
            "character_id": character_id,
            "changed_at_chapter": {"$gt": since_chapter, "$lte": to_chapter}
        },
        fields=["field_changed", "old_value", "new_value", "changed_at_chapter"],
        sort={"changed_at_chapter": 1}
    )

# Delta Query - Knowledge Acquired
def get_knowledge_delta(
    character_id: str,
    since_chapter: int
) -> WorkingSetQuery:
    """Get knowledge acquired by character since specific chapter"""
    
    return WorkingSetQuery(
        collection="character_knowledge_matrix",
        filters={
            "character_id": character_id,
            "acquired_at_chapter": {"$gt": since_chapter}
        },
        fields=["information_item_id", "status", "acquired_at_chapter"],
        sort={"acquired_at_chapter": 1}
    )
```

---

## Caching Strategy

### Hot Data Cache (In-Memory)

Cache frequently accessed data with TTL:

```python
from functools import lru_cache
from datetime import datetime, timedelta

class WorldBibleCache:
    def __init__(self, ttl_seconds: int = 300):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        self.cache[key] = (value, datetime.now())
    
    def invalidate_chapter(self, chapter: int):
        """Invalidate cache entries for specific chapter"""
        keys_to_remove = [
            k for k in self.cache.keys()
            if f"chapter_{chapter}" in k
        ]
        for k in keys_to_remove:
            del self.cache[k]

# Cache key patterns
# character:eddard_stark:chapter:7
# thread:active:pov:eddard_stark:chapter:7
# consequences:eddard_stark:chapter:7
```

### Cache Invalidation Rules

1. **After scene completion:** Invalidate working set cache for POV character
2. **After chapter completion:** Invalidate all chapter-specific caches
3. **After World Bible update:** Invalidate affected entity caches
4. **TTL expiration:** Automatic cleanup of stale entries

---

## Query Optimization Guidelines

### Index Usage

Always use indexes for:
- Character ID lookups
- Chapter-based range queries
- Status + window queries (consequences, payoffs)
- Relationship lookups

### Aggregation Pipeline

For complex working sets, use aggregation:

```python
# Example: Get POV character with their active threads
def get_pov_with_threads(pov_character: str, chapter: int):
    pipeline = [
        # Match character
        {"$match": {"character_id": pov_character}},
        
        # Lookup active threads
        {"$lookup": {
            "from": "plot_thread_registry",
            "localField": "character_id",
            "foreignField": "characters_involved",
            "as": "active_threads",
            "pipeline": [
                {"$match": {"status": "Active"}}
            ]
        }},
        
        # Project fields
        {"$project": {
            "full_name": 1,
            "emotional_state": 1,
            "active_threads.thread_id": 1,
            "active_threads.thread_name": 1
        }}
    ]
    
    return db.character_directory.aggregate(pipeline)
```

---

## Error Handling

### Missing Data Scenarios

```python
class WorldBibleError(Exception):
    pass

class EntityNotFoundError(WorldBibleError):
    """Raised when character, thread, or other entity doesn't exist"""
    pass

class InvalidChapterError(WorldBibleError):
    """Raised when querying chapter that doesn't exist"""
    pass

def safe_get_working_set(query: WorkingSetQuery) -> List[Dict]:
    """Execute query with error handling"""
    try:
        results = interface.get_working_set(query)
        if not results:
            logger.warning(f"Empty result for query: {query}")
        return results
    except pymongo.errors.PyMongoError as e:
        logger.error(f"Database error: {e}")
        raise WorldBibleError(f"Failed to retrieve {query.collection}") from e
```

---

## Summary: Working Set Sizes

| Use Case | Typical Documents | Typical Size | vs Full Module |
|----------|------------------|--------------|----------------|
| Gardener Plotting | 10-20 | 6-8KB | 90% reduction |
| Scene Construction | 5-15 | 4-6KB | 85% reduction |
| POV Consistency | 3-10 | 2-4KB | 95% reduction |
| Character Integration | 10-30 | 8-12KB | 80% reduction |
| Consequence Cascade | 5-15 | 5-8KB | 85% reduction |
| Braided Narrative | 5-10 | 4-6KB | 90% reduction |

**Average data transfer per skill invocation: 5-10KB** (vs 50-200KB for full modules)

---

## API Surface Summary

```python
class WorldBibleAPI:
    """Complete API for World Bible retrieval"""
    
    # Core working set queries
    def get_gardener_working_set(pov, chapter) -> Dict
    def get_scene_construction_working_set(pov, participants, location, chapter) -> Dict
    def get_pov_consistency_working_set(pov, participants, chapter) -> Dict
    def get_character_integration_working_set(characters, chapter) -> Dict
    def get_consequence_cascade_working_set(event, chapter, affected) -> Dict
    def get_braided_narrative_working_set(povs, chapter, lookback) -> Dict
    
    # Delta queries
    def get_character_delta(character, since_chapter, to_chapter) -> Dict
    def get_knowledge_delta(character, since_chapter) -> Dict
    def get_thread_delta(since_chapter) -> Dict
    
    # Utility
    def get_character_at_chapter(character, chapter) -> Dict
    def get_chapter_summary(chapter) -> Dict
    def get_timeline_slice(start_day, end_day) -> List[Dict]
```

# Orchestrator Agent - NoSQL Interactions

## Overview

This document defines the interaction patterns between the main writing/orchestration agent and the NoSQL World Bible storage. It covers:

1. **Read patterns** - How the orchestrator queries working sets for skills
2. **Write patterns** - How the orchestrator persists updates after skill execution
3. **Transaction boundaries** - What constitutes a consistent update unit
4. **Caching and consistency** - How the orchestrator maintains coherent state

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Orchestrator Agent                           │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐ │
│  │   Session   │  │   Context    │  │   World Bible           │ │
│  │   State     │  │   Manager    │  │   Interface             │ │
│  │             │  │              │  │                         │ │
│  │ - Current   │  │ - T1/T2/T3   │  │ - Query builder         │ │
│  │   chapter   │  │   tiers      │  │ - Update batcher        │ │
│  │ - Active    │  │ - Scene      │  │ - Cache manager         │ │
│  │   scenes    │  │   checkpoint │  │ - Consistency checker   │ │
│  │ - Working   │  │              │  │                         │ │
│  │   set cache │  │              │  │                         │ │
│  └─────────────┘  └──────────────┘  └─────────────────────────┘ │
│           │               │                    │                │
│           └───────────────┴────────────────────┘                │
│                          │                                      │
│           ┌──────────────┴──────────────┐                       │
│           ▼                             ▼                       │
│  ┌─────────────────┐         ┌──────────────────┐              │
│  │  Sub-agents/    │         │   NoSQL Database │              │
│  │  Skills         │         │                  │              │
│  │                 │         │   - All World    │              │
│  │ - Receive       │         │     Bible        │              │
│  │   working sets  │         │     collections  │              │
│  │ - Return        │         │                  │              │
│  │   outputs       │         │                  │              │
│  │                 │         │                  │              │
│  └─────────────────┘         └──────────────────┘              │
│                                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Principles

### 1. **Orchestrator is Sole World Bible Accessor**

From `grrm_agent_specs.md` Section 2, Governing Rules:
> Skills do not access the World Bible directly. They receive **curated excerpts** passed by the main agent.

**Implication:** All database queries and updates flow through the orchestrator.

### 2. **Lazy Loading for Working Sets**

Working sets are loaded **just-in-time** for skill invocation, not prefetched.

**Benefits:**
- Context only contains data currently needed
- Reduces memory footprint
- Enables targeted cache invalidation

### 3. **Write Batching**

World Bible updates are batched and written at defined transaction boundaries:
- After scene acceptance (not after each skill)
- After chapter completion (major checkpoint)

**Benefits:**
- Atomic updates ensure consistency
- Reduces write amplification
- Enables rollback on regeneration

---

## Read Patterns

### Pattern 1: Skill Invocation Query

**When:** Before invoking any skill that needs World Bible data

**Flow:**

```python
class Orchestrator:
    def invoke_skill_with_working_set(
        self,
        skill_name: str,
        current_chapter: int,
        current_scene: int,
        pov_character: str
    ) -> SkillOutput:
        
        # 1. Determine required working set
        working_set_spec = self.get_working_set_spec(skill_name)
        
        # 2. Build and execute queries
        working_set = {}
        for component in working_set_spec.required_components:
            query = self.wb_interface.build_query(
                component=component,
                context={
                    "chapter": current_chapter,
                    "scene": current_scene,
                    "pov_character": pov_character,
                    "working_set_cache": self.working_set_cache
                }
            )
            
            # Check cache first
            cache_key = f"{component}:{current_chapter}:{pov_character}"
            cached = self.cache.get(cache_key)
            
            if cached and not self.is_cache_stale(component, current_scene):
                working_set[component] = cached
            else:
                # Query from database
                result = self.wb_interface.execute_query(query)
                working_set[component] = result
                self.cache.set(cache_key, result)
        
        # 3. Invoke skill with working set
        skill_output = self.skill_router.invoke(
            skill_name=skill_name,
            working_set=working_set,
            additional_context={
                "last_scene_outcome": self.get_last_scene_outcome(),
                "user_instructions": self.user_instructions
            }
        )
        
        # 4. Store output (for potential World Bible updates)
        self.pending_skill_outputs[skill_name] = skill_output
        
        return skill_output
```

**Working Set Specifications by Skill:**

| Skill | Required Components | Query Pattern Reference |
|-------|--------------------|-------------------------|
| Gardener Plotting System | POV state, POV knowledge, active threads, active consequences, approaching bombs, pending payoffs | `world-bible-retrieval.md#get_gardener_working_set` |
| Scene Construction | POV profile, relationships, location, political context, culture | `world-bible-retrieval.md#get_scene_construction_working_set` |
| POV Consistency Maintenance | POV knowledge, others' knowledge, voice profile | `world-bible-retrieval.md#get_pov_consistency_working_set` |
| Character Integration | Character records, relationships, political state | `world-bible-retrieval.md#get_character_integration_working_set` |
| Consequence Cascade | Existing consequences, active bombs, relationships, cascades | `world-bible-retrieval.md#get_consequence_cascade_working_set` |
| Braided Narrative | Recent chapters, shared threads, timeline sync | `world-bible-retrieval.md#get_braided_narrative_working_set` |

---

### Pattern 2: Session Initialization Query

**When:** At the start of a new writing session

**Purpose:** Load minimal working set for chapter continuity

```python
def initialize_session(self, chapter_number: int, pov_character: str):
    """Load initial working set for chapter start"""
    
    # 1. Get previous chapter summary
    previous_chapter = self.wb_interface.get_chapter_summary(chapter_number - 1)
    
    # 2. Get POV character state
    pov_state = self.wb_interface.get_character_state(
        character_id=pov_character,
        chapter=chapter_number - 1  # State at end of previous chapter
    )
    
    # 3. Get active threads for this POV
    active_threads = self.wb_interface.get_working_set(
        WorkingSetQuery(
            collection="plot_thread_registry",
            filters={
                "characters_involved": pov_character,
                "status": "Active"
            },
            fields=["thread_id", "thread_name", "expected_convergence"]
        )
    )
    
    # 4. Store in session state
    self.session_state = {
        "current_chapter": chapter_number,
        "pov_character": pov_character,
        "previous_chapter": previous_chapter,
        "pov_state": pov_state,
        "active_threads": active_threads,
        "scenes_completed": [],
        "current_scene": 1
    }
```

---

### Pattern 3: Delta Refresh Query

**When:** After World Bible updates, refresh stale cache entries

```python
def refresh_working_set_after_update(
    self,
    updated_entities: List[str],
    chapter: int
):
    """Refresh cache entries affected by updates"""
    
    for entity in updated_entities:
        # Determine which working set components are affected
        affected_components = self.map_entity_to_components(entity)
        
        for component in affected_components:
            # Invalidate cache
            cache_key = f"{component}:{chapter}:{self.session_state['pov_character']}"
            self.cache.invalidate(cache_key)
            
            # Optionally: Preload fresh data
            if component in self.eager_load_components:
                query = self.wb_interface.build_query(
                    component=component,
                    context={"chapter": chapter}
                )
                fresh_data = self.wb_interface.execute_query(query)
                self.cache.set(cache_key, fresh_data)
```

---

## Write Patterns

### Pattern 1: Scene Acceptance Update

**When:** User accepts a scene draft

**Transaction Scope:** Single scene's impact on World Bible

```python
def on_scene_accepted(
    self,
    scene_number: int,
    scene_draft: str,
    skill_outputs: Dict[str, SkillOutput]
):
    """Persist World Bible updates after scene acceptance"""
    
    # 1. Extract World Bible updates from skill outputs
    updates = self.extract_wb_updates(skill_outputs)
    
    # 2. Build update batch
    update_batch = UpdateBatch(
        chapter=self.session_state["current_chapter"],
        scene=scene_number,
        updates=updates
    )
    
    # 3. Validate updates (contradiction check)
    validation_result = self.wb_interface.validate_updates(update_batch)
    if not validation_result.is_valid:
        self.handle_validation_failure(validation_result)
        return
    
    # 4. Execute atomic update
    try:
        with self.wb_interface.transaction() as txn:
            # 4.1 Character state updates
            for char_update in updates.character_updates:
                txn.update_character_state(char_update)
            
            # 4.2 Knowledge matrix updates
            for knowledge_update in updates.knowledge_updates:
                txn.insert_knowledge_state(knowledge_update)
            
            # 4.3 Relationship updates
            for rel_update in updates.relationship_updates:
                txn.update_relationship(rel_update)
            
            # 4.4 Timeline updates
            txn.update_timeline({
                "chapter": self.session_state["current_chapter"],
                "scene": scene_number,
                "events": updates.timeline_events
            })
            
            # 4.5 Plot thread updates
            for thread_update in updates.thread_updates:
                txn.update_thread_status(thread_update)
            
            # 4.6 Consequence updates
            for consequence_update in updates.consequence_updates:
                txn.update_consequence_chain(consequence_update)
            
            # 4.7 Archive scene draft
            draft_ref = txn.archive_scene_draft(
                chapter=self.session_state["current_chapter"],
                scene=scene_number,
                draft=scene_draft
            )
            
        # 5. Commit transaction
        txn.commit()
        
    except Exception as e:
        txn.rollback()
        raise WorldBibleUpdateError(f"Failed to persist scene {scene_number}") from e
    
    # 6. Update session state
    self.session_state["scenes_completed"].append({
        "scene_number": scene_number,
        "summary": updates.scene_summary,
        "draft_ref": draft_ref,
        "world_bible_changes": updates.get_changed_fields()
    })
    
    # 7. Refresh working set cache
    self.refresh_working_set_after_update(
        updated_entities=updates.get_affected_entities(),
        chapter=self.session_state["current_chapter"]
    )
    
    # 8. Clear pending skill outputs
    self.pending_skill_outputs.clear()
```

**Update Batch Structure:**

```python
@dataclass
class WorldBibleUpdateBatch:
    chapter: int
    scene: int
    
    # Character state changes
    character_updates: List[CharacterStateUpdate]
    
    # Knowledge changes
    knowledge_updates: List[KnowledgeUpdate]
    
    # Relationship changes
    relationship_updates: List[RelationshipUpdate]
    
    # Timeline events
    timeline_events: List[TimelineEvent]
    
    # Plot thread changes
    thread_updates: List[PlotThreadUpdate]
    
    # Consequence changes
    consequence_updates: List[ConsequenceUpdate]
    
    # Scene metadata
    scene_summary: str
    
    def get_affected_entities(self) -> List[str]:
        """Return list of entity IDs affected by this batch"""
        entities = set()
        for update in self.character_updates:
            entities.add(update.character_id)
        for update in self.knowledge_updates:
            entities.add(update.character_id)
        # ... etc
        return list(entities)
```

---

### Pattern 2: Chapter Completion Checkpoint

**When:** All scenes in chapter are accepted

**Transaction Scope:** Full chapter commit + checkpoint creation

```python
def on_chapter_completed(self, chapter_number: int):
    """Persist chapter completion and create checkpoint"""
    
    # 1. Finalize POV chapter log
    chapter_log = {
        "chapter_number": chapter_number,
        "pov_character": self.session_state["pov_character"],
        "scenes": self.session_state["scenes_completed"],
        "cliffhanger": self.determine_cliffhanger(),
        "connections": self.identify_connections(),
        "chapter_delta": self.aggregate_deltas()
    }
    
    try:
        with self.wb_interface.transaction() as txn:
            # 2. Insert chapter log
            txn.insert_chapter_log(chapter_log)
            
            # 3. Update character POV counts
            txn.update_character_pov_count(
                character_id=self.session_state["pov_character"],
                chapter=chapter_number
            )
            
            # 4. Create chapter snapshot for versioned collections
            txn.create_chapter_snapshot(chapter_number)
            
            # 5. Update any pending payoff statuses
            for payoff in self.identify_paid_off_setups():
                txn.update_payoff_status(
                    setup_id=payoff.setup_id,
                    status="Paid off",
                    chapter=chapter_number
                )
            
            # 6. Archive full chapter draft
            txn.archive_chapter_draft(
                chapter=chapter_number,
                scenes=[s["draft_ref"] for s in self.session_state["scenes_completed"]]
            )
            
        txn.commit()
        
    except Exception as e:
        txn.rollback()
        raise ChapterCommitError(f"Failed to commit chapter {chapter_number}") from e
    
    # 7. Clear session state (clean slate for next chapter)
    self.clear_session_state()
    
    # 8. Clear all working set caches
    self.cache.clear_all()
    
    logger.info(f"Chapter {chapter_number} committed successfully")
```

---

### Pattern 3: Scene Regeneration Rollback

**When:** User requests scene regeneration

**Transaction Scope:** Revert World Bible to pre-scene state

```python
def on_scene_regeneration_requested(
    self,
    scene_number: int,
    feedback: UserFeedback
):
    """Handle scene regeneration - rollback World Bible state"""
    
    # 1. Find previous checkpoint for this scene
    previous_checkpoint = self.find_scene_checkpoint(scene_number)
    
    if not previous_checkpoint:
        # No previous accepted version - just clear pending updates
        self.clear_pending_updates_for_scene(scene_number)
        return
    
    # 2. Rollback World Bible to checkpoint state
    try:
        with self.wb_interface.transaction() as txn:
            # 2.1 Revert character states
            for char_state in previous_checkpoint.character_states:
                txn.restore_character_state(
                    character_id=char_state.character_id,
                    state=char_state,
                    chapter=self.session_state["current_chapter"]
                )
            
            # 2.2 Revert knowledge matrix
            txn.delete_knowledge_acquired_after(
                chapter=self.session_state["current_chapter"],
                scene=scene_number
            )
            
            # 2.3 Revert relationship changes
            for rel_state in previous_checkpoint.relationship_states:
                txn.restore_relationship_state(rel_state)
            
            # 2.4 Revert consequence updates
            txn.delete_consequences_added_in(
                chapter=self.session_state["current_chapter"],
                scene=scene_number
            )
            
        txn.commit()
        
    except Exception as e:
        txn.rollback()
        raise RollbackError(f"Failed to rollback scene {scene_number}") from e
    
    # 3. Clear working set cache (stale after rollback)
    self.cache.clear_all()
    
    # 4. Store feedback for regeneration guidance
    self.regeneration_feedback = feedback
```

---

## Consistency and Validation

### Contradiction Detection

Before any write, validate against existing state:

```python
class ConsistencyValidator:
    def validate_update_batch(self, batch: UpdateBatch) -> ValidationResult:
        """Check for contradictions before commit"""
        
        contradictions = []
        
        # 1. Knowledge consistency
        for knowledge_update in batch.knowledge_updates:
            existing = self.wb_interface.get_knowledge_state(
                character_id=knowledge_update.character_id,
                information_item=knowledge_update.information_item_id
            )
            
            if existing and existing.status == "KNOWS":
                # Character already knows this - check for contradiction
                if knowledge_update.new_status == "DOES_NOT_KNOW":
                    contradictions.append(Contradiction(
                        type="Knowledge",
                        description=f"{knowledge_update.character_id} already knows {knowledge_update.information_item_id}",
                        severity="Error"
                    ))
        
        # 2. Physical consistency
        for char_update in batch.character_updates:
            if "current_location" in char_update.changed_fields:
                # Check if location change is plausible given timeline
                if not self.is_location_change_plausible(char_update):
                    contradictions.append(Contradiction(
                        type="Timeline",
                        description=f"Impossible location change for {char_update.character_id}",
                        severity="Warning"
                    ))
        
        # 3. Timeline consistency
        for event in batch.timeline_events:
            if not self.is_event_chronologically_valid(event):
                contradictions.append(Contradiction(
                    type="Timeline",
                    description=f"Event {event.event_id} violates timeline",
                    severity="Error"
                ))
        
        return ValidationResult(
            is_valid=len([c for c in contradictions if c.severity == "Error"]) == 0,
            contradictions=contradictions
        )
```

---

## Caching Strategy

### Cache Tiers

```python
class OrchestratorCache:
    def __init__(self):
        # L1: Hot cache (in-memory, per-session)
        self.hot_cache = {}  # TTL: 5 minutes
        
        # L2: Chapter cache (persistent, per-chapter)
        self.chapter_cache = ChapterCache()
        
        # L3: External cache (Redis/Memcached for cross-session)
        self.external_cache = ExternalCache()
    
    def get_working_set(self, key: str, level: int = 1):
        # Try L1
        if level >= 1 and key in self.hot_cache:
            return self.hot_cache[key]
        
        # Try L2
        if level >= 2:
            value = self.chapter_cache.get(key)
            if value:
                self.hot_cache[key] = value  # Promote to L1
                return value
        
        # Try L3
        if level >= 3:
            value = self.external_cache.get(key)
            if value:
                self.chapter_cache.set(key, value)  # Promote to L2
                self.hot_cache[key] = value  # Promote to L1
                return value
        
        return None
```

### Cache Invalidation Rules

| Event | Invalidation Action |
|-------|---------------------|
| Scene accepted | Invalidate POV character cache entries |
| Scene regenerated | Clear all working set caches |
| Chapter completed | Clear all caches + archive chapter cache |
| User feedback received | Invalidate affected scene's cached data |
| External update (admin) | Full cache flush |

---

## Error Handling and Recovery

### Database Connection Failures

```python
class ResilientWBInterface:
    def __init__(self, mongo_client):
        self.client = mongo_client
        self.retry_policy = ExponentialBackoff(
            max_retries=3,
            base_delay=1.0,
            max_delay=10.0
        )
    
    def execute_with_retry(self, operation):
        """Execute database operation with retry logic"""
        for attempt in range(self.retry_policy.max_retries):
            try:
                return operation()
            except pymongo.errors.ConnectionFailure as e:
                if attempt < self.retry_policy.max_retries - 1:
                    delay = self.retry_policy.get_delay(attempt)
                    logger.warning(f"Connection failed, retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    raise DatabaseUnavailableError() from e
```

### Transaction Failures

```python
def safe_transaction(self, operations):
    """Execute operations with rollback on failure"""
    txn = self.wb_interface.start_transaction()
    
    try:
        for op in operations:
            op.execute(txn)
        
        txn.commit()
        
    except Exception as e:
        logger.error(f"Transaction failed: {e}")
        txn.rollback()
        
        # Notify orchestrator
        raise TransactionRollbackError(
            f"Rolled back {len(operations)} operations",
            failed_operation=op
        ) from e
```

---

## Performance Guidelines

### Query Optimization

1. **Use projection always** - Never select *
2. **Prefer exact matches** - Use indexed fields for filters
3. **Limit result sets** - Add limit() when possible
4. **Batch updates** - Use bulk_write() for multiple updates

### Example: Optimized Batch Update

```python
def batch_update_character_states(self, updates: List[CharacterStateUpdate]):
    """Efficiently batch multiple character updates"""
    
    bulk_ops = []
    for update in updates:
        bulk_ops.append(
            pymongo.UpdateOne(
                {"character_id": update.character_id},
                {
                    "$set": {
                        "emotional_state": update.emotional_state,
                        "active_desires": update.active_desires,
                        "updated_at": datetime.now(),
                        "version": update.new_version
                    },
                    "$addToSet": {
                        "appears_in_chapters": update.chapter
                    }
                }
            )
        )
    
    result = self.db.character_directory.bulk_write(bulk_ops)
    return result.modified_count
```

---

## API Summary

```python
class OrchestratorWBAPI:
    """Complete API for orchestrator-World Bible interactions"""
    
    # Read operations
    def load_working_set_for_skill(skill_name: str, context: Dict) -> Dict
    def get_character_state(character_id: str, chapter: int) -> Dict
    def get_chapter_summary(chapter: int) -> Dict
    def query_timeline_slice(start_day: int, end_day: int) -> List[Dict]
    
    # Write operations
    def apply_scene_updates(scene_number: int, skill_outputs: Dict)
    def commit_chapter_checkpoint(chapter_number: int)
    def rollback_scene_changes(scene_number: int)
    
    # Validation
    def validate_update_batch(batch: UpdateBatch) -> ValidationResult
    def check_contradictions(proposed_updates: Dict) -> List[Contradiction]
    
    # Cache management
    def refresh_cache(affected_entities: List[str])
    def clear_all_caches()
    
    # Transaction control
    def start_transaction() -> Transaction
    def commit_transaction(txn: Transaction)
    def rollback_transaction(txn: Transaction)
```

---

## Implementation Checklist

- [ ] Implement `WorldBibleInterface` class with query builder
- [ ] Implement `UpdateBatch` and validation logic
- [ ] Implement transaction wrapper with rollback support
- [ ] Implement caching layer with tiered strategy
- [ ] Implement contradiction detection for common cases
- [ ] Add retry logic for database operations
- [ ] Add logging for all World Bible interactions
- [ ] Add metrics for query performance
- [ ] Create integration tests for transaction rollback
- [ ] Document query patterns for each skill

---
name: worldbuilding
description: Builds the physical, political, cultural, religious, and magical architecture of the story world using the iceberg principle — ten times more is constructed than will be shown on the page. Invoked once after Defining Rough Endpoints, before the character pipeline begins. For targeted world expansion mid-story, the planning_subagent queries existing Story State KG records first. Returns structured world data in artifacts for persistence via story_state_manager into Story State Modules 3.1–3.5.
---

# Worldbuilding

## Identity

**Purpose:** Construct the world the story inhabits. Not to fill it with exposition, but to make the author confident in every detail a POV character will notice, filter, and misunderstand. The iceberg principle governs everything: what appears on the page is the visible tip; the depth beneath it is what makes the surface feel real.

---

## Core

Build geography, political landscape, cultures, religion, and magic system using the iceberg principle — construct ten times more than will be shown. Return structured world data in artifacts for Story State Modules 3.1–3.5. The world must feel like a consequence of itself: geography shapes politics, politics shapes culture, culture shapes religion, religion shapes the magic system's relationship to society.

---

## Input

### From brain context (`worker_request.context`)

#### Required

1. **`endpoint_compass`** — The final compass document from the Pass 2 output of `defining-rough-endpoints`. Contains: prologue specification, starting situation, ending destination, milestones, core conflict question, compass notes, genre, themes.

#### Optional

2. **`research_output`** — Structured research notes from a prior `research-integration` delegation, when the brain judged that factual grounding was needed for specific domains before worldbuilding could proceed.

3. **`expansion_scope`** — When invoked for **targeted world expansion** mid-story (a new region is introduced, a new culture is encountered), the brain passes the specific domain(s) to expand and the chapter context. The planning_subagent then queries the KG before building.

4. **`chapter_context`** — Current chapter number. Required for targeted expansion; used to scope KG queries with `as_of_chapter`.

### Fetched from Story State KG

**Initial worldbuilding (project start):** No KG queries needed — no world data exists yet.

**Targeted world expansion (mid-story):** The planning_subagent queries existing records to ensure new material is consistent with what has already been established:

```
# Existing political map
query_kg_nodes({type: "Faction"}, as_of_chapter=chapter_context)
query_kg_nodes({type: "Location"}, as_of_chapter=chapter_context)

# Existing cultural/religious records
query_kg_nodes({type: "Culture"}, as_of_chapter=chapter_context)

# Existing magic system state
query_kg_nodes({type: "MagicSystem"}, as_of_chapter=chapter_context)

# Existing history records
query_kg_nodes({type: "Event", "properties.is_historical": true},
               as_of_chapter=chapter_context)
```

These queries ensure that new world elements do not contradict established Story State records. If any query returns results, those records are treated as constraints on new construction.

---

## Output

All output is returned in `artifacts`. The brain routes persistence to `story_state_manager`.

### `artifacts` structure

```json
{
  "political_power_map": [
    {
      "node_type": "Faction",
      "properties": {
        "name": "<territory or power centre name>",
        "core_values": ["..."],
        "military_assets": "<description>",
        "economic_assets": "<description>"
      },
      "iceberg_notes": {
        "current_controller": "<character or faction>",
        "allegiances": "<current alliances and stability>",
        "active_enmities": "<conflicts and phase>",
        "internal_tensions": "<fractures and vulnerabilities>",
        "what_this_power_does_not_know": "<blind spots>"
      }
    }
  ],
  "geography": [
    {
      "node_type": "Location",
      "properties": {
        "name": "<official and colloquial names>",
        "description": "<sensory physical description>",
        "climate": "<seasonal norms>",
        "seasonal_weather_state": "<current state>"
      },
      "iceberg_notes": {
        "adjacent_locations": "<routes and travel times>",
        "what_the_geography_makes_difficult": "<constraints on movement, agriculture, war>",
        "cultural_meaning": "<how inhabitants have been shaped by it>"
      }
    }
  ],
  "cultures_customs_religion": [
    {
      "node_type": "Culture",
      "properties": {
        "name": "<culture or institution name>",
        "core_values": ["..."],
        "core_fears": ["..."],
        "key_customs": ["..."],
        "class_structure": "<description>",
        "gender_dynamics": "<description>",
        "religious_beliefs": "<description>",
        "political_power": "<institutional influence>",
        "languages_dialects": ["..."]
      },
      "iceberg_notes": {
        "internal_contradictions": "<what the culture believes about itself that is not true>"
      }
    }
  ],
  "history_and_legends": [
    {
      "node_type": "Event",
      "properties": {
        "name": "<how it is commonly known>",
        "summary": "<brief summary>",
        "is_historical": true,
        "true_account": "<what actually happened>",
        "believed_account": "<what characters generally believe>",
        "factional_interpretations": {"faction_name": "interpretation"},
        "physical_remnants": ["<ruins, artifacts, locations>"],
        "story_significance": "<why this matters to the current narrative>",
        "referenced_in_chapters": []
      }
    }
  ],
  "magic_system": {
    "node_type": "MagicSystem",
    "properties": {
      "prevalence": "Rare | Increasing | Decreasing | Stable",
      "confirmed_capabilities": ["..."],
      "confirmed_limits": ["..."],
      "confirmed_costs": ["..."],
      "unexplained_phenomena": ["..."],
      "recent_magical_events": []
    },
    "iceberg_notes": {
      "nature_of_magic": "<ontological description>",
      "known_practitioners": "<who can use it; societal view>",
      "institutional_relationship": "<how political/religious power has responded>"
    }
  },
  "location_connections": [
    {
      "edge_type": "CONNECTED_TO",
      "from_node": "<location_logical_id>",
      "to_node": "<location_logical_id>",
      "properties": {
        "distance": "<description>",
        "travel_times": {"foot": "...", "horse": "...", "ship": "..."}
      }
    }
  ]
}
```

The KG-typed records in `political_power_map`, `geography`, `cultures_customs_religion`, `history_and_legends`, and `magic_system` are structured for direct insertion by `story_state_manager`. `iceberg_notes` fields contain narrative context for the planning_subagent's use; `story_state_manager` may store these in a `notes` property or ignore them depending on schema.

---

## Examples

For worked examples of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## Iceberg Principle

For each domain, the output must contain substantially more than will appear in the story. The visible surface — what a POV character notices and what the prose renders — should feel inevitable, not arbitrary. Inevitability comes from the depth beneath it.

**Test:** For any world detail that will appear on the page, three questions must be answerable from the output: *Why is it this way? What would change it? Who benefits from it remaining as it is?* If the output cannot answer those three questions, the iceberg is not deep enough.

---

## Boundary

- **Does not** write prose, scenes, or narrative description. Returns structured data.
- **Does not** create character records. Character Conception in `character_subagent` reads existing Story State records as its world context; this skill provides that material but does not create characters.
- **Does not** plot scenes or assign events. Worldbuilding is background architecture, not plot.
- **Does not** write to the Story State KG. Returns structured world data in artifacts for `story_state_manager` to persist.
- **Does not** invoke Research Integration. The brain decides when research is needed and passes its output in context.
- **Does not** produce an exhaustive encyclopaedia. Depth of understanding, not length of record. If a detail has no bearing on any plausible story event, it does not belong in the output.

---

## Invocation

The `planning_subagent` invokes this skill when the brain delegates world construction:

- **Initial invocation (project start):** Once, after the brain has confirmed the final compass from Pass 2 of `defining-rough-endpoints` and persisted the initial plot thread seeds. The brain passes the final compass in context. This is invoked before the character pipeline begins — `character_subagent`'s Character Conception reads the resulting Story State records as world context.

- **Targeted expansion (mid-story):** When a new region or culture is introduced and needs a record. The brain passes the compass plus `expansion_scope` and `chapter_context`. The planning_subagent queries existing KG records first to identify constraints.

- **Reassess scenario:** If the Reassess Trigger fires and the world architecture is the source of the problem, the brain re-delegates with the full original compass plus preservation constraints.

---

## Story State Interface

| Direction | Details |
|---|---|
| **Queries from Story State KG** | Initial: none. Targeted expansion: Faction, Location, Culture, MagicSystem, and historical Event nodes queried with `as_of_chapter` to identify constraints on new construction |
| **Returns in artifacts** | KG-ready node records for Faction, Location, Culture, historical Event, and MagicSystem nodes; CONNECTED_TO edge records for geography; `iceberg_notes` for narrative depth. Brain routes to `story_state_manager` for persistence into Story State Modules 3.1–3.5 |

---

## Dependencies

**Upstream:** Brain provides `endpoint_compass` from prior `defining-rough-endpoints` Pass 2 artifacts. Optionally: `research_output` from prior `research-integration` artifacts. For targeted expansion: existing Story State records queried directly.

**Downstream:** World data records returned in artifacts. The brain routes these to `story_state_manager` for persistence. After persistence, Story State Module 3.1 (Faction nodes representing the political map) is available to `character_subagent`'s Character Conception skill as world context — the brain passes relevant KG query results in the character conception context dict.

---

## Instructions

### Step 1 — Internalise the compass

Read the endpoint compass fully before constructing anything. The world must feel like the natural habitat of this story — the political landscape, geography, and cultural tensions should make the starting situation legible and the milestones plausible. Ask: *What kind of world makes this story inevitable?*

### Step 2 — For targeted expansion: query existing records

If `expansion_scope` is present in context, query the KG before building anything new. Read existing Faction, Location, Culture, MagicSystem, and historical Event nodes at `as_of_chapter`. Treat existing records as constraints — new material must be consistent with what has already been established and written into prose.

### Step 3 — Establish geography first

Geography is the foundation. Political power is shaped by it. Culture is adapted to it. Magic systems interact with it. Build geography before politics or culture; let the physical reality constrain what can exist.

Work through each significant location the compass implies — where the story starts, where milestones are likely to occur, the broader region they sit within. Apply the iceberg: know more about each place than will be rendered.

### Step 4 — Build political and power structures from geography

Given the geography, ask: *Who controls what, and why?* Power follows from geography (control of routes, resources, defensible positions), from history (conquest, inheritance, religious sanction), and from current capacity (armies, wealth, legitimacy). Build each power centre as a consequence of the physical world and its own history.

Flag internal tensions: no power structure is stable. What is under pressure? Who wants what, and from whom?

### Step 5 — Develop cultures and religion as consequences of geography and politics

Culture is how people adapt to and make meaning from where they live and who rules them. Religion is how they explain what they cannot control. Build each culture and institution as a consequence of the geography and political landscape already established — not as a free-floating set of customs.

Flag the internal contradictions: what does this culture believe about itself that is not true?

### Step 6 — Layer history and legend

Every political and cultural reality has a history that made it. Identify the 2–4 historical events most relevant to the current story situation. For each, establish the true account (author-level knowledge) and the believed account (what characters generally accept). Identify factional disputes where relevant.

Physical remnants matter: the ruins, artifacts, and surviving practices that make the past present.

### Step 7 — Define the magic system

Build the magic system as a consequence of the world already established — its nature, distribution, costs, and institutional relationships must make sense given the geography, politics, culture, and history. A magic system that could be dropped into any world is not yet a worldbuilding output; it must be specific to *this* world.

Apply the iceberg: establish capabilities, limits, and costs with precision. Leave space for unexplained phenomena — the mysteries a POV character encounters that even the world's own scholars cannot account for.

### Step 8 — Apply the iceberg test

Before assembling output, apply the three-question iceberg test to each significant world detail: *Why is it this way? What would change it? Who benefits from it remaining as it is?* If the output cannot answer, deepen the relevant section.

### Step 9 — Assemble artifacts and return

Assemble KG-ready node records for all five domains. Include `location_connections` edge records for geography. Return with `status: "success"`.

---

## Quality Checks

Before returning output, verify:

- [ ] Geography was established before politics and culture.
- [ ] Each Faction/power structure has at least one internal tension in `iceberg_notes`.
- [ ] Each Culture has at least one internal contradiction in `iceberg_notes`.
- [ ] History is present: at least 2–4 historical Event records with `true_account` and `believed_account`.
- [ ] MagicSystem record is specific to this world — nature and costs reflect the geography, culture, and history built.
- [ ] Iceberg test applied: three questions answerable for all major world details.
- [ ] All records structured as KG-ready node/edge documents.
- [ ] No prose written. No characters created. No plot events specified.
- [ ] No Story State KG writes from this skill — all output in artifacts for story_state_manager.
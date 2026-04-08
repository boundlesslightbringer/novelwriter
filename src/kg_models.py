from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# ==========================================
# Base Models
# ==========================================

class KGNodeBase(BaseModel):
    """Base model for all Knowledge Graph Nodes."""
    logical_id: str = Field(description="The stable identifier for the entity (e.g., 'char_jon_snow').")
    type: str = Field(description="The type of node.")
    valid_from: int = Field(description="The chapter number when this node becomes active.")
    properties: Dict[str, Any] = Field(description="Type-specific attributes.")


class KGEdgeBase(BaseModel):
    """Base model for all Knowledge Graph Edges."""
    logical_id: str = Field(description="The stable identifier for the relationship.")
    type: str = Field(description="The type of relationship.")
    from_node: str = Field(description="The logical_id of the source node.")
    to_node: str = Field(description="The logical_id of the target node.")
    valid_from: int = Field(description="The chapter number when this edge becomes active.")
    properties: Dict[str, Any] = Field(description="Relationship-specific attributes.")


# ==========================================
# Node Property Models
# ==========================================

class CharacterProperties(BaseModel):
    full_name: str
    aliases: List[str] = Field(default_factory=list)
    age: Optional[int] = None
    gender: Optional[str] = None
    physical_description: Optional[str] = None
    faction: Optional[str] = None
    rank: Optional[str] = None
    occupation: Optional[str] = None
    public_vs_private_reputation: Optional[str] = None
    location: Optional[str] = None
    surface_beliefs: List[str] = Field(default_factory=list)
    core_wound: Optional[str] = None
    core_desire: Optional[str] = None
    core_fear: Optional[str] = None
    self_deception: Optional[str] = None
    values_under_pressure: List[str] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)
    response_patterns: Dict[str, Any] = Field(default_factory=dict)
    arc_type: Optional[str] = None
    arc_stage: Optional[str] = None
    pov_eligible: bool = False
    pov_chapter_count: int = 0
    last_pov_chapter: Optional[int] = None
    injuries_physical_state: List[str] = Field(default_factory=list)
    emotional_state: Optional[str] = None


class LocationProperties(BaseModel):
    name: str
    description: Optional[str] = None
    climate: Optional[str] = None
    seasonal_weather_state: Optional[str] = None


class EventProperties(BaseModel):
    name: str
    absolute_date: Optional[str] = None
    summary: str
    is_historical: bool = False
    true_account: Optional[str] = None
    believed_account: Optional[str] = None
    factional_interpretations: Dict[str, str] = Field(default_factory=dict)
    physical_remnants: List[str] = Field(default_factory=list)
    story_significance: Optional[str] = None
    referenced_in_chapters: List[int] = Field(default_factory=list)


class FactionProperties(BaseModel):
    name: str
    core_values: List[str] = Field(default_factory=list)
    military_assets: Optional[str] = None
    economic_assets: Optional[str] = None


class CultureProperties(BaseModel):
    name: str
    core_values: List[str] = Field(default_factory=list)
    core_fears: List[str] = Field(default_factory=list)
    key_customs: List[str] = Field(default_factory=list)
    class_structure: Optional[str] = None
    gender_dynamics: Optional[str] = None
    religious_beliefs: Optional[str] = None
    political_power: Optional[str] = None
    languages_dialects: List[str] = Field(default_factory=list)


class KnowledgeItemProperties(BaseModel):
    description: str


class PlotThreadProperties(BaseModel):
    name: str
    status: Literal["Active", "Dormant", "Resolved", "Abandoned"]
    originating_chapter: int
    expected_convergence_window: Optional[str] = None
    resolution_summary: Optional[str] = None
    abandonment_rationale: Optional[str] = None


class PayoffProperties(BaseModel):
    type: Literal["Chekhov's gun", "Foreshadowing", "Consequence bomb", "Prophecy", "In-world legend"]
    description: str
    planted_in_chapter: int
    narrative_phase_anchor: Literal["early", "mid", "convergence", "final act"]
    detonation_trigger: str
    resolution_status: Literal["Pending", "Paid off", "Overdue"]
    priority_tier: Literal["Essential", "Enriching", "Unclassified"]
    dual_register: bool = False


class ChapterProperties(BaseModel):
    chapter_number: int
    pov_character: str
    location: str
    scene_summary: str
    cliffhanger_status: Optional[str] = None
    connections: List[str] = Field(default_factory=list)
    chapter_delta: Optional[str] = None


class MagicSystemProperties(BaseModel):
    prevalence: Literal["Rare", "Increasing", "Decreasing", "Stable"]
    confirmed_capabilities: List[str] = Field(default_factory=list)
    confirmed_limits: List[str] = Field(default_factory=list)
    confirmed_costs: List[str] = Field(default_factory=list)
    unexplained_phenomena: List[str] = Field(default_factory=list)
    recent_magical_events: List[str] = Field(default_factory=list)


class CascadeChainProperties(BaseModel):
    sequence: List[str] = Field(default_factory=list)
    current_position: str
    remaining_links: List[str] = Field(default_factory=list)


class PhysicalDetailProperties(BaseModel):
    subject_id: str
    detail: str
    established_in_chapter: int
    last_referenced_in_chapter: Optional[int] = None


class ContradictionProperties(BaseModel):
    nature: Literal["Physical", "Logical", "Knowledge", "Timeline"]
    description: str
    detected_at_chapter: int
    resolution_status: Literal["Unresolved", "Resolved", "Accepted as intentional ambiguity"]
    resolution_notes: Optional[str] = None


# ==========================================
# Edge Property Models
# ==========================================

class KnowsProperties(BaseModel):
    status: Literal["KNOWS", "BELIEVES", "SUSPECTS", "DOES NOT KNOW"]
    acquired_at_chapter: int
    source: Optional[str] = None
    dramatic_irony_flag: bool = False


class RelationshipProperties(BaseModel):
    emotional_valence: str
    power_dynamic: str
    history: Optional[str] = None
    secrets_kept: List[str] = Field(default_factory=list)
    trajectory: Optional[str] = None
    convergence_potential: Optional[str] = None
    most_recent_interaction: Optional[str] = None


class LocatedAtProperties(BaseModel):
    arrival_chapter: int
    departure_date: Optional[str] = None
    arrival_date: Optional[str] = None
    travel_duration: Optional[str] = None


class CausesProperties(BaseModel):
    consequence_type: Literal["Immediate", "Short-term", "Long-term"]
    cascade_chain_id: Optional[str] = None


class ControlsProperties(BaseModel):
    held_since_chapter: int
    stability_rating: str


class InvolvesProperties(BaseModel):
    role: str


class PaysOffInProperties(BaseModel):
    payoff_chapter: int


class AllianceProperties(BaseModel):
    established_in_chapter: int
    stability: str


class ConnectedToProperties(BaseModel):
    distance: str
    travel_times: Dict[str, str] = Field(default_factory=dict)


class BelongsToCultureProperties(BaseModel):
    role: str


class DependsOnProperties(BaseModel):
    dependency_type: str


class DescribesProperties(BaseModel):
    relevance: str


class InformedProperties(BaseModel):
    knowledge_item_id: str
    chapter_reference: int
    method: Literal["Spoken", "Written", "Overheard", "Inferred"]


class ConflictsWithProperties(BaseModel):
    conflict_side: str


# ==========================================
# Tool Argument Schemas
# ==========================================

class AddNodeArgs(BaseModel):
    logical_id: str = Field(description="The stable identifier for the entity (e.g., 'char_jon_snow').")
    node_type: Literal[
        "Character", "Location", "Event", "Faction", "Culture", "KnowledgeItem",
        "PlotThread", "Payoff", "Chapter", "MagicSystem", "CascadeChain",
        "PhysicalDetail", "Contradiction"
    ] = Field(description="The type of node.")
    properties: Dict[str, Any] = Field(description="The type-specific attributes of the node.")
    chapter: int = Field(description="The chapter number when this node becomes active.")


class UpdateNodeArgs(BaseModel):
    logical_id: str = Field(description="The stable identifier for the entity.")
    updated_properties: Dict[str, Any] = Field(description="The new properties to apply (merged with existing).")
    chapter: int = Field(description="The chapter number when this update occurs.")


class AddEdgeArgs(BaseModel):
    logical_id: str = Field(description="The stable identifier for the relationship.")
    edge_type: Literal[
        "KNOWS", "RELATIONSHIP", "LOCATED_AT", "CAUSES", "CONTROLS", "INVOLVES",
        "PAYS_OFF_IN", "ALLIED_WITH", "AT_WAR_WITH", "CONNECTED_TO",
        "BELONGS_TO_CULTURE", "DEPENDS_ON", "DESCRIBES", "INFORMED", "CONFLICTS_WITH"
    ] = Field(description="The type of relationship.")
    from_node: str = Field(description="The logical_id of the source node.")
    to_node: str = Field(description="The logical_id of the target node.")
    properties: Dict[str, Any] = Field(description="The relationship-specific attributes.")
    chapter: int = Field(description="The chapter number when this edge becomes active.")


class UpdateEdgeArgs(BaseModel):
    logical_id: str = Field(description="The stable identifier for the relationship.")
    updated_properties: Dict[str, Any] = Field(description="The new properties to apply (merged with existing).")
    chapter: int = Field(description="The chapter number when this update occurs.")


class QueryNodesArgs(BaseModel):
    query: Dict[str, Any] = Field(description="MongoDB query dictionary (e.g., {'type': 'Character', 'properties.faction': 'Stark'}).")
    as_of_chapter: Optional[int] = Field(default=None, description="If provided, retrieves the state of nodes as they existed at this chapter.")
    sort: Optional[Dict[str, int]] = Field(default=None, description="Optional sort dictionary (e.g., {'properties.chapter_number': 1}).")


class QueryEdgesArgs(BaseModel):
    query: Dict[str, Any] = Field(description="MongoDB query dictionary (e.g., {'type': 'KNOWS', 'from': 'char_arya'}).")
    as_of_chapter: Optional[int] = Field(default=None, description="If provided, retrieves the state of edges as they existed at this chapter.")
    sort: Optional[Dict[str, int]] = Field(default=None, description="Optional sort dictionary (e.g., {'properties.chapter_number': 1}).")


class ProposedUpdate(BaseModel):
    action: Literal["add_node", "update_node", "add_edge", "update_edge"]
    logical_id: str


class DetectContradictionArgs(BaseModel):
    proposed_updates: List[ProposedUpdate] = Field(description="A list of proposed update dictionaries.")
    chapter: int = Field(description="The chapter number at which the updates are proposed.")

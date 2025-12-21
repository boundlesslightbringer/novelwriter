from pydantic import BaseModel

class GenreDetermination(BaseModel):
    """
    Example output:
    {
        "reasoning": "The text exhibits classic high fantasy elements: a medieval setting with multiple fantasy races (dragonborn, orcs, Yuan-Ti), active deities with specific domains (Great Mother Tamara), a formal magic system manifesting as divine healing and glowing runic tattoos, and epic combat with named magical weapons. The tone is heroic and mythic, featuring archetypal characters including a warrior-king champion blessed by gods and a priest-healer brother. Technology is strictly pre-gunpowder (zweihanders, greataxes, leather/scale armor). The world-building includes specific geographic locations and racial histories, creating a clear secondary world with moral dichotomies between 'civilized' dragonborn and 'barbaric' orcs. These elements collectively align with High Fantasy conventions, particularly reminiscent of Dungeons & Dragons-inspired fiction.",
        "genre": "High Fantasy"
    """

    reasoning: str
    genre: str


class ExtractedAndClassifiedEntity(BaseModel):
    """
    Example output:
    {"name": "Shedinn", "category": "Person", "significance": "Major"}
    """

    name: str
    category: str
    significance: str


class EntityExtractionAndClassification(BaseModel):
    """
    Example output:
    [
        {"name": "Shedinn", "category": "Person", "significance": "Major"},
        {"name": "Great Mother Tamara", "category": "Person", "significance": "Supporting"},
        {"name": "Shalash", "category": "Person", "significance": "Minor"},
        {"name": "Balasar", "category": "Person", "significance": "Major"},
        {"name": "Daedendrainn clan", "category": "Organization", "significance": "Supporting"},
        {"name": "Ssarki", "category": "Person", "significance": "Supporting"},
        {"name": "Yuan-Ti", "category": "Organization", "significance": "Minor"},
        {"name": "Orc warchief", "category": "Person", "significance": "Supporting"},
        {"name": "Shesten highlands", "category": "Location", "significance": "Supporting"},
        {"name": "Ranhas shore", "category": "Location", "significance": "Supporting"},
        {"name": "Aass-Nag jungle", "category": "Location", "significance": "Minor"},
        {"name": "Tymras lowlands", "category": "Location", "significance": "Supporting"},
        {"name": "Javok", "category": "Object", "significance": "Major"},
        {"name": "Orc horde", "category": "Organization", "significance": "Supporting"},
        {"name": "Dragonborn", "category": "Other", "significance": "Supporting"},
        {"name": "The Gods", "category": "Person", "significance": "Supporting"}
    ]
    """

    entities: list[ExtractedAndClassifiedEntity]


class PersonProfile(BaseModel):
    """
    Example output:
    {
        "name": "{entity_name}",
        "titles_and_nicknames": ["great servant of Tamara", "mighty"],
        "role": "Legendary Ancestor",
        "physical_description": None,
        "history": "Ancestral figure of the Daedendrainn clan. Revered as a 'great servant' of the Great Mother Tamara, the dragon Goddess of life, mercy, and healing. Invoked in prayer by Shedinn as a source of strength for his brother Balasar.",
        "personality": None,
        "voice_style": None,
        "motivations": None,
        "strengths": None,
        "flaws": None,
        "long_term_goals": None,
        "short_term_goals": None,
        "current_internal_state": None,
    }

    """

    name: str
    titles_and_nicknames: list[str] | None
    role: str
    physical_description: str | None
    history: str | None
    personality: str | None
    voice_style: str | None
    motivations: str | None
    strengths: str | None
    flaws: str | None
    long_term_goals: str | None
    short_term_goals: str | None
    current_internal_state: str | None


class LocationProfile(BaseModel):
    """
    {
    "primary_name": "Aass-Nag",
    "secondary_name": null,
    "description": "Aass-Nag is a treacherous jungle realm where oppressive humidity and unbearable heat saturate the air beneath a dense canopy that chokes out most direct sunlight.",
    "history": "Aass-Nag's most significant historical marker is the death of Ssarki, a beloved friend of King Balasar of the Daedendrainn clan, who fell victim to a treacherous Yuan-Ti ambush within the jungle's depths long ago.",
    "prominent_entities_associated": ["Ssarki", "Yuan-Ti"]
    }
    """

    primary_name: str
    secondary_name: str | None
    description: str | None
    history: str | None
    prominent_entities_associated: list[str] | None


class EventProfile(BaseModel):
    """
    Example output:
    """

    primary_name: str
    secondary_name: str | None
    description: str | None
    history: str | None
    prominent_entities_associated: list[str] | None


class ObjectProfile(BaseModel):
    """
    Example output:
    {
    "name": "Javok",
    "type": "Weapon (Heavy Zweihander)",
    "description": "A massive two-handed greatsword of substantial weight, forged for the towering physique of a dragonborn chieftain.",
    "history": "Javok was gifted to Balasar of the Daedendrainn by his dearest companion, Ssarki, forging a bond that would transcend death.",
    "magical_properties": "The blade channels the lingering spirit of Ssarki, manifesting as conjured flame.",
    "owner": "Balasar of the Daedendrainn clan, Chieftain and King of the Shesten highlands and Ranhas shore."
    }
    """

    primary_name: str
    secondary_name: str | None
    type: str | None
    description: str | None
    history: str | None
    magical_properties: str | None
    owner: str | None


class OrganizationProfile(BaseModel):
    """
    {
    "name": "Daedendrainn clan",
    "type": "Clan",
    "description": "A dragonborn warrior clan that venerates the Great Mother Tamara, goddess of life, mercy, and healing.",
    "history": "The Daedendrainn clan claims divine lineage through the blood of Shalash, a legendary servant of the dragon goddess Tamara, which forms the core of their identity and ruling legitimacy.",
    "goals": "Stated: To defend their territories and champion the values of life, order, and peace under Tamara's divine guidance, protecting the world from destructive, subjugation-oriented forces. Actual: To maintain and expand territorial hegemony, establish regional dominance through military supremacy, uphold clan honor and divine mandate via conquest, and secure their position as the preeminent power in their domain.",
    "prominent_members": ["Balasar (Chieftain-King)", "Shedinn (Healer and Prince)", "Shalash (Legendary Ancestor-Founder)", "Ssarki (Fallen Warrior, Honored Dead)"]
    }
    """

    primary_name: str
    secondary_name: str | None
    type: str | None
    description: str | None
    history: str | None
    goals: str | None
    prominent_members: list[str] | None


# class ExtractedRelationships(BaseModel):
#     source: str
#     target: str
#     relation_type: str
#     dynamics: str


# class RelationshipExtractor(BaseModel):
#     relationships: list[ExtractedRelationships]
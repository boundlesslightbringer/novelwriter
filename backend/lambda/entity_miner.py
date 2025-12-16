import json
import re
import logging
import ast
from pydantic import BaseModel
import boto3
from concurrent.futures import ThreadPoolExecutor, as_completed
import chromadb
import datetime

import os

# Configure logging
logger = logging.getLogger()
# logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)


def lambda_handler(event, context):
    # TODO implement
    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}


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


class EntityMiningWorkflow:
    def __init__(self):
        logger.info("Initializing EntityMiningWorkflow")
        # Try to find config.json in the current directory or lambda directory
        config_path = "config.json"
        if not os.path.exists(config_path):
            # Try lambda directory
            lambda_config_path = os.path.join(os.path.dirname(__file__), "config.json")
            if os.path.exists(lambda_config_path):
                config_path = lambda_config_path
            else:
                raise FileNotFoundError(
                    f"config.json not found in current directory or {os.path.dirname(__file__)}"
                )

        with open(config_path, "r") as f:
            self.config = json.load(f)

        dynamodb = boto3.resource(
            "dynamodb", region_name=self.config.get("aws").get("region")
        )

        self.bedrock_runtime = boto3.client(
            "bedrock-runtime", region_name=self.config.get("aws").get("region")
        )

        self.model_id = self.config.get("aws").get("entity_miner_model_id")
        if not self.model_id:
            raise ValueError("entity_miner_model_id not found in config.json")

        self.prompt_template_table = dynamodb.Table(
            self.config.get("aws").get("dynamodb_table")
        )

        self.global_prompt_templates_novel_name = self.config.get("aws").get(
            "dynamodb_table_global_prompt_templates_novel_name"
        )
        model_cfg = self.config.get("model", {})
        self.model_temperature = model_cfg.get("temperature", 0)
        self.model_top_p = model_cfg.get("top_p", 0.9)
        self.model_seed = model_cfg.get("seed", 69420)
        self.fetch_workflow_prompt_templates()
        self.initialize_chroma(local=True)
        logger.info("EntityMiningWorkflow initialized")

    def initialize_chroma(self, local: bool = False) -> None:
        try:
            if local:
                self.chroma_client = chromadb.HttpClient(
                    host="localhost",
                    port=8000,
                )
            else:
                self.chroma_client = chromadb.HttpClient(
                    host=self.config.get("chroma").get("host"),
                    port=self.config.get("chroma").get("port"),
                    settings=chromadb.Settings(anonymized_telemetry=False)
                )
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise e

        try:
            self.chroma_collection = self.chroma_client.get_or_create_collection(
                name=self.config.get("chroma").get("default_collection")
            )
        except Exception as e:
            logger.error(f"Error getting ChromaDB collection: {e}")
            raise e

    def fetch_workflow_prompt_templates(self) -> None:
        logger.info("Fetching workflow prompt templates")
        self.genre_determination_prompt_template = self._fetch_template(
            "entity_miner_genre_determination", "genre determination"
        )
        self.entity_extraction_and_classification_prompt_template = (
            self._fetch_template(
                "entity_miner_entity_extraction_and_classification", "entity extraction"
            )
        )
        self.person_profiler_prompt_template = self._fetch_template(
            "entity_miner_person_profiler", "person profiler"
        )
        self.location_profiler_prompt_template = self._fetch_template(
            "entity_miner_location_profiler", "location profiler"
        )
        self.event_profiler_prompt_template = self._fetch_template(
            "entity_miner_event_profiler", "event profiler"
        )
        self.object_profiler_prompt_template = self._fetch_template(
            "entity_miner_object_profiler", "object profiler"
        )
        self.organization_profiler_prompt_template = self._fetch_template(
            "entity_miner_organization_profiler", "organization profiler"
        )
        self.relationship_extractor_prompt_template = self._fetch_template(
            "entity_miner_relationship_extraction", "relationship extraction"
        )

        self.profile_config = {
            "Person": {
                "template": self.person_profiler_prompt_template,
                "schema": PersonProfile,
                "label": "person_profile",
            },
            "Location": {
                "template": self.location_profiler_prompt_template,
                "schema": LocationProfile,
                "label": "location_profile",
            },
            "Event": {
                "template": self.event_profiler_prompt_template,
                "schema": EventProfile,
                "label": "event_profile",
            },
            "Object": {
                "template": self.object_profiler_prompt_template,
                "schema": ObjectProfile,
                "label": "object_profile",
            },
            "Organization": {
                "template": self.organization_profiler_prompt_template,
                "schema": OrganizationProfile,
                "label": "organization_profile",
            },
        }

    def _fetch_template(self, template_type: str, label: str) -> dict:
        try:
            response = self.prompt_template_table.get_item(
                Key={"novel_name": "global", "template_type": template_type}
            )
            item = response.get("Item", {})
            if not item:
                logger.warning(f"{label} template not found in DynamoDB")
            return item
        except Exception as e:
            logger.error(f"Error fetching {label} prompt template: {e}")
            return {}

    def invoke_model(
        self,
        model_id: str,
        system_prompt: str,
        instruction_prompt: str,
        temperature: float = 0,
        top_p: float = 0.9,
        seed: int = 69420,  # default seed for reproducibility
    ):
        if not model_id:
            logger.error("model_id is None or empty")
            raise ValueError("model_id cannot be None or empty")
        if not system_prompt or not instruction_prompt:
            logger.error("system_prompt or instruction_prompt is None or empty")
            raise ValueError(
                "system_prompt and instruction_prompt cannot be None or empty"
            )

        logger.info(f"model_id: {model_id}")
        logger.info(f"Invoking model: {model_id}")
        try:
            body = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": instruction_prompt},
                ],
                "temperature": temperature,
                "top_p": top_p,
                "seed": seed,
            }
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType="application/json",
            )
            return response
        except Exception as e:
            logger.error(f"Error invoking model: {e}")
            raise

    def _parse_response(
        self,
        response,
        model_output_schema: BaseModel,
    ) -> BaseModel:
        content = (
            json.loads(response.get("body").read())
            .get("choices")[0]
            .get("message")
            .get("content")
        )
        # logger.info(f"Response content:\n{content}\n")
        
        extracted_json = content.split("```json")[-1].split("```")[0]

        parsed = json.loads(extracted_json)

        # # extract the json from the response
        # pattern = r"```json\s*(.*?)\s*```"
        # matches = re.findall(pattern, content, re.DOTALL)

        # if not matches:
        #     # Fallback: Try finding a block without the "json" language tag
        #     # strictly at the end of the string if the tagged version fails.
        #     fallback_pattern = r"```\s*(\{.*?\})\s*```"
        #     matches = re.findall(fallback_pattern, content, re.DOTALL)

        # if matches:
        #     extracted_json = matches[-1].strip()
            
        #     try:
        #         # Parse to ensure it's valid JSON
        #         parsed = json.loads(extracted_json)
        #     except json.JSONDecodeError:
        #     # If JSON parsing fails, ast.literal_eval to handle single quotes
        #         try:
        #             parsed = ast.literal_eval(extracted_json)
        #         except (ValueError, SyntaxError):
        #             # Re-raise the original JSON error if both fail
        #             raise
        # else:
        #     raise ValueError("No JSON found in the response")

        # If the schema expects an object but the model returned a bare list, wrap it.
        if model_output_schema is EntityExtractionAndClassification and isinstance(
            parsed, list
        ):
            parsed = {"entities": parsed}

        logger.info(f"Response JSON parsed:\n{parsed}\n")
        return model_output_schema.model_validate(parsed)

    @staticmethod
    def _get_prompts(template: dict, label: str) -> tuple[str, str]:
        system_prompt = template.get("system_prompt_template")
        instruction_prompt = template.get("instruction_prompt_template")
        if not system_prompt or not instruction_prompt:
            raise ValueError(
                f"Missing prompts for {label}: system_prompt_template or instruction_prompt_template is empty"
            )
        return system_prompt, instruction_prompt

    def extract_genre(self, text: str) -> GenreDetermination:
        system_prompt, instruction_prompt = self._get_prompts(
            self.genre_determination_prompt_template, "genre_determination"
        )

        instruction_prompt = instruction_prompt.format(text=text)

        response = self.invoke_model(
            model_id=self.model_id,
            system_prompt=system_prompt,
            instruction_prompt=instruction_prompt,
        )
        return self._parse_response(response, GenreDetermination)

    def extract_entities(
        self, text: str, genre: str
    ) -> EntityExtractionAndClassification:
        system_prompt, instruction_prompt = self._get_prompts(
            self.entity_extraction_and_classification_prompt_template,
            "entity_extraction_and_classification",
        )

        instruction_prompt = instruction_prompt.format(genre=genre, text=text)

        response = self.invoke_model(
            model_id=self.model_id,
            system_prompt=system_prompt,
            instruction_prompt=instruction_prompt,
        )
        return self._parse_response(response, EntityExtractionAndClassification)

    def profile_entity(
        self, text: str, entity_name: str, genre: str, category: str, significance: str = None
    ) -> BaseModel:
        if category not in self.profile_config:
            logger.warning(f"No profiler configured for category: {category}")
            return None

        config = self.profile_config[category]
        system_prompt, instruction_prompt = self._get_prompts(
            config["template"], config["label"]
        )


        if category == "Person": 
            if significance == "Minor":
                pass
            else:
                instruction_prompt = instruction_prompt.format(
                    entity_name=entity_name, genre=genre, text=text, significance=significance
                )
        else:
            instruction_prompt = instruction_prompt.format(
                entity_name=entity_name, genre=genre, text=text
            )

        response = self.invoke_model(
        model_id=self.model_id,
        system_prompt=system_prompt,
        instruction_prompt=instruction_prompt,
        )

        return self._parse_response(response, config["schema"])

    # def extract_relationships(self, text: str) -> RelationshipExtractor:
    #     system_prompt, instruction_prompt = self._get_prompts(
    #         self.relationship_extractor_prompt_template, "relationship_extraction"
    #     )
    #     response = self.invoke_model(
    #         model_id=self.model_id,
    #         system_prompt=system_prompt,
    #         instruction_prompt=instruction_prompt,
    #     )
    #     return self._parse_response(response, RelationshipExtractor)

    def execute(self, text: str) -> dict:
        logger.info("Starting entity mining execution")
        genre_result = self.extract_genre(text=text)
        if genre_result is None:
            raise ValueError("Failed to extract genre")
        genre = genre_result.genre
        logger.info(f"Genre determined: {genre}")

        extracted_entities = self.extract_entities(text=text, genre=genre)
        if extracted_entities is None:
            raise ValueError("Failed to extract entities")
        logger.info(f"Extracted {len(extracted_entities.entities)} entities")

        profiled_entities = []
        with ThreadPoolExecutor(
            max_workers=10  # len(extracted_entities.entities) 10 is the AWS Bedrock maximum concurrent requests
        ) as executor:
            futures = [
                executor.submit(
                    self.profile_entity, text=text, entity_name=entity.name, genre=genre, category=entity.category, significance=entity.significance if entity.significance else None
                )
                for entity in extracted_entities.entities
            ]
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        profiled_entities.append(result)
                except Exception as e:
                    logger.error(f"Error profiling entity: {e}")

        # relationships = self.extract_relationships(text) TODO: need a separate process for extracting and determining the relationships between the entities
        logger.info("Entity mining execution completed")
        return {
            "genre": genre,
            "genre_determination_reasoning": genre_result.reasoning,
            "profiled_entities": profiled_entities,
            # "relationships": relationships
        }

    def save_entities_to_chroma(
        self, entity_profiles: list[BaseModel], genre: str, novel_name: str
    ) -> None:
        doc_ids = []
        for profile in entity_profiles:
            try:
                doc_id = f"{novel_name}-{profile.name}"
            except AttributeError as ae:
                doc_id = f"{novel_name}-{profile.primary_name}"
            doc_ids.append(doc_id)
                
        self.chroma_collection.add(
            documents=[profile.model_dump_json() for profile in entity_profiles],
            metadatas=[{"genre": genre, "novel_name": novel_name, "source": "entity_miner"} for profile in entity_profiles],
            ids=doc_ids,
        )
        logger.info(f"Saved {len(entity_profiles)} entity profiles to ChromaDB")


if __name__ == "__main__":
    # Try to find nadarr_prologue.txt in the current directory or lambda directory
    prologue_path = "nadarr_prologue.txt"
    if not os.path.exists(prologue_path):
        # Try lambda directory
        lambda_prologue_path = os.path.join(os.path.dirname(__file__), "nadarr_prologue.txt")
        if os.path.exists(lambda_prologue_path):
            prologue_path = lambda_prologue_path
        else:
            # Try stories directory (relative to workspace root)
            stories_prologue_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "stories",
                "nadarr_prologue.txt"
            )
            if os.path.exists(stories_prologue_path):
                prologue_path = stories_prologue_path
            else:
                raise FileNotFoundError(
                    f"nadarr_prologue.txt not found in current directory, {os.path.dirname(__file__)}, or {stories_prologue_path}"
                )
    
    with open(prologue_path, "r") as f:
        text = f.read()
    entity_miner = EntityMiningWorkflow()
    result = entity_miner.execute(text)
    # print(result)
    entity_miner.save_entities_to_chroma(result["profiled_entities"], result["genre"], "abs_prologue")
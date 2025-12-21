import datetime
import hashlib
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import boto3
import chromadb
from pydantic import BaseModel
from pydantic_models import GenreDetermination, EntityExtractionAndClassification, PersonProfile, LocationProfile, EventProfile, ObjectProfile, OrganizationProfile

# Configure logging
logger = logging.getLogger()
# logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)


def load_config():
    try:
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
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise

    with open(config_path) as f:
        config = json.load(f)

    return config

class EntityMiningWorkflow:
    def __init__(
        self,
        local_chroma: bool = False,
        chroma_collection_name: str = None,
        model_temperature: float = 0,
        model_top_p: float = 0.9,
        model_seed: int = 69420,
    ):
        logger.info("Initializing EntityMiningWorkflow")

        self.config = load_config()

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

        self.model_temperature = model_temperature
        self.model_top_p = model_top_p
        self.model_seed = model_seed

        self.fetch_workflow_prompt_templates()

        self.initialize_chroma(
            local=local_chroma, collection_name=chroma_collection_name
        )

        logger.info("EntityMiningWorkflow initialized")

    def initialize_chroma(
        self, local: bool = False, collection_name: str = None
    ) -> None:
        try:
            if local:
                self.chroma_client = chromadb.HttpClient(
                    host=self.config.get("chroma").get("local").get("host"),
                    port=self.config.get("chroma").get("local").get("port"),
                    settings=chromadb.Settings(anonymized_telemetry=False),
                )
            else:
                self.chroma_client = chromadb.HttpClient(
                    host=self.config.get("chroma").get("remote").get("host"),
                    port=self.config.get("chroma").get("remote").get("port"),
                    settings=chromadb.Settings(anonymized_telemetry=False),
                )
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise e

        try:
            if not collection_name:
                collection_name = self.config.get("chroma").get("default_collection")

            self.chroma_collection = self.chroma_client.get_or_create_collection(
                name=collection_name
            )
        except Exception as e:
            logger.error(f"Error fetching or creating ChromaDB collection: {e}")
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

        # If the schema expects an object but the model returned a bare list, wrap it.
        if model_output_schema is EntityExtractionAndClassification and isinstance(
            parsed, list
        ):
            parsed = {"entities": parsed}

        # logger.info(f"Response JSON parsed:\n{parsed}\n")
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
        self,
        text: str,
        entity_name: str,
        genre: str,
        category: str,
        significance: str = None,
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
                    entity_name=entity_name,
                    genre=genre,
                    text=text,
                    significance=significance,
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
            max_workers=10  # 10 is the maximum concurrent requests that can be made to AWS Bedrock 
        ) as executor:
            futures = [
                executor.submit(
                    self.profile_entity,
                    text=text,
                    entity_name=entity.name,
                    genre=genre,
                    category=entity.category,
                    significance=entity.significance if entity.significance else None,
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

        # TODO: might need a separate process for extracting and determining the relationships between the entities
        # relationships = self.extract_relationships(text) 

        logger.info("Entity mining execution completed")
        return {
            "genre": genre,
            "genre_determination_reasoning": genre_result.reasoning,
            "profiled_entities": profiled_entities,
        }

    def save_entities_to_chroma(
        self, entity_profiles: list[BaseModel], genre: str, novel_name: str
    ) -> bool:
        try:
            doc_ids = []
            for profile in entity_profiles:
                try:
                    doc_id = f"{novel_name}-{profile.name}"
                except AttributeError:
                    doc_id = f"{novel_name}-{profile.primary_name}"
                doc_ids.append(doc_id)

            self.chroma_collection.add(
                documents=[profile.model_dump_json() for profile in entity_profiles],
                metadatas=[
                    {
                        "novel_name": novel_name,
                        "genre": genre,
                        "source": "entity_miner",
                        "created_at": datetime.datetime.now().isoformat(),
                    }
                    for profile in entity_profiles
                ],
                ids=doc_ids,
            )
            logger.info(f"Saved {len(entity_profiles)} entity profiles to ChromaDB")
        except Exception as e:
            logger.error(f"Error saving entities to ChromaDB: {e}")
            return False

        return True


def lambda_handler(event, context):
    """
    event should contain a dictionary with the following keys:
    - novel_name: str
    - text: str
    - username: str
    """
    result = None

    # check if event source is S3 trigger
    if "Records" in event and event["Records"][0]["eventSource"] == "aws:s3":
        # get the S3 bucket name and key
        bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
        key = event["Records"][0]["s3"]["object"]["key"]
        # event_type = event["Records"][0]["eventName"]


        config = load_config()
        s3_client = boto3.client("s3", region_name=config.get("aws").get("region"))
        try:
            file_object = s3_client.get_object(Bucket=bucket_name, Key=key)
            file_object_metadata = file_object["Metadata"]
            story_text = file_object["Body"].read().decode("utf-8")
            novel_name = key.split("/")[-1].split(".")[0]
            username = file_object_metadata.get("username")
            last_modified_ts = file_object_metadata.get("last_modified")
            story_text_hash = file_object_metadata.get("story_text_hash")

            if story_text_hash == hashlib.sha256(story_text.encode("utf-8")).hexdigest() or last_modified_ts < datetime.now() - datetime.timedelta(minutes=10):
                logger.warning("Story text has not changed since last modification or last modification is more than 10 minutes ago")
                return {
                    "status": "no change",
                    "num_mined_entities": 0,
                }

        except s3_client.exceptions.NoSuchKey:
            raise ValueError(f"Object '{key}' not found in bucket '{bucket_name}'") from s3_client.exceptions.NoSuchKey
        except Exception as e:
            logger.error(f"S3 Error: {e}")
            raise ValueError(f"S3 Error: {e}") from e


    # synchronous trigger called via React frontend
    else:  
        story_text = event.get("text")
        novel_name = event.get("novel_name")
        username = event.get("username")

    entity_miner = EntityMiningWorkflow(
        novel_name=novel_name, chroma_collection_name=f"{username}-{novel_name}"
    )

    mined_entities = entity_miner.execute(story_text)
    saved_to_chroma = entity_miner.save_entities_to_chroma(
        mined_entities["profiled_entities"], mined_entities["genre"], novel_name
    )

    result = {
        "status": "success" if saved_to_chroma else "error",
        "num_mined_entities": len(mined_entities["profiled_entities"]),
    }

    return result


if __name__ == "__main__":
    # Try to find nadarr_prologue.txt in the current directory or lambda directory
    prologue_path = "stories/nadarr_prologue.txt"
    if not os.path.exists(prologue_path):
        # Try lambda directory
        lambda_prologue_path = os.path.join(
            os.path.dirname(__file__), "nadarr_prologue.txt"
        )
        if os.path.exists(lambda_prologue_path):
            prologue_path = lambda_prologue_path
        else:
            # Try stories directory (relative to workspace root)
            stories_prologue_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "stories",
                "nadarr_prologue.txt",
            )
            if os.path.exists(stories_prologue_path):
                prologue_path = stories_prologue_path
            else:
                raise FileNotFoundError(
                    f"nadarr_prologue.txt not found in current directory, {os.path.dirname(__file__)}, or {stories_prologue_path}"
                )

    with open(prologue_path) as f:
        text = f.read()
    entity_miner = EntityMiningWorkflow(local_chroma=True)
    result = entity_miner.execute(text)
    # print(result)
    entity_miner.save_entities_to_chroma(
        result["profiled_entities"], result["genre"], "abs_prologue"
    )

import datetime
import hashlib
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tkinter import E

import boto3
import chromadb
from opentelemetry import context, trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.aws_lambda import AwsLambdaInstrumentor
from opentelemetry.instrumentation.botocore import BotocoreInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.threading import ThreadingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace import Status, StatusCode
from pydantic import BaseModel

from pydantic_models import (
    EntityExtractionAndClassification,
    EventProfile,
    GenreDetermination,
    LocationProfile,
    ObjectProfile,
    OrganizationProfile,
    PersonProfile,
)

# Configure logging
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

tracer = None


def load_config():
    try:
        config_path = "config.json"
        if not os.path.exists(config_path):
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


def setup_otel():
    resource = Resource.create(
        {
            "service.name": "entity-miner",
            "service.namespace": "novelwriter",
        }
    )

    provider = TracerProvider(resource=resource)

    exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
    )

    provider.add_span_processor(BatchSpanProcessor(exporter))
    # For local runs to see the traces in the console
    # provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)

    # Instrumentation Setup
    LoggingInstrumentor().instrument(set_logging_format=True)
    BotocoreInstrumentor().instrument()
    ThreadingInstrumentor().instrument()

    return trace.get_tracer("entity_miner")

tracer = setup_otel()

class EntityMiningWorkflow:
    def __init__(
        self,
        novel_name: str,
        local_chroma: bool = False,
        chroma_collection_name: str = None,
        model_temperature: float = 0,
        model_top_p: float = 0.9,
        model_seed: int = 69420,
    ):
        with tracer.start_as_current_span("entity_mining_workflow_init") as span:
            span.set_attribute("novel.name", novel_name)
            span.set_attribute("chroma.local", local_chroma)
            span.set_attribute("chroma.collection_name", chroma_collection_name or "default")
            span.set_attribute("model.temperature", model_temperature)
            span.set_attribute("model.top_p", model_top_p)
            span.set_attribute("model.seed", model_seed)

            logger.info("Initializing EntityMiningWorkflow")

            self.config = load_config()

            dynamodb = boto3.resource("dynamodb", region_name=self.config.get("aws").get("region"))

            self.bedrock_runtime = boto3.client(
                "bedrock-runtime", region_name=self.config.get("aws").get("region")
            )

            self.model_id = self.config.get("aws").get("entity_miner_model_id")
            if not self.model_id:
                raise ValueError("entity_miner_model_id not found in config.json")

            span.set_attribute("gen_ai.request.model", self.model_id)

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

            self.initialize_chroma(local=local_chroma, collection_name=chroma_collection_name)

            span.set_attribute("init.status", "success")
            logger.info("EntityMiningWorkflow initialized")

    def initialize_chroma(self, local: bool = False, collection_name: str = None) -> None:
        with tracer.start_as_current_span("initialize_chroma_client") as span:
            span.set_attribute("chroma.client.local", local)

            try:
                config_key = "local" if local else "remote"
                host = self.config.get("chroma").get(config_key).get("host")
                port = self.config.get("chroma").get(config_key).get("port")
                span.set_attribute("chroma.host", host)
                span.set_attribute("chroma.port", port)

                self.chroma_client = chromadb.HttpClient(
                    host=host,
                    port=port,
                    settings=chromadb.Settings(anonymized_telemetry=False),
                )
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, "Failed to initialize ChromaDB client"))
                logger.error(f"Error initializing ChromaDB: {e}")
                raise e

            try:
                if not collection_name:
                    collection_name = self.config.get("chroma").get("default_collection")

                span.set_attribute("chroma.collection_name", collection_name)
                self.chroma_collection = self.chroma_client.get_or_create_collection(
                    name=collection_name
                )
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, "Failed to get/create collection"))
                logger.error(f"Error fetching or creating ChromaDB collection: {e}")
                raise e

    def fetch_workflow_prompt_templates(self) -> None:
        with tracer.start_as_current_span("fetch_workflow_prompt_templates") as span:
            logger.info("Fetching workflow prompt templates")

            templates_to_fetch = [
                (
                    "entity_miner_genre_determination",
                    "genre determination",
                    "genre_determination_prompt_template",
                ),
                (
                    "entity_miner_entity_extraction_and_classification",
                    "entity extraction",
                    "entity_extraction_and_classification_prompt_template",
                ),
                (
                    "entity_miner_person_profiler",
                    "person profiler",
                    "person_profiler_prompt_template",
                ),
                (
                    "entity_miner_location_profiler",
                    "location profiler",
                    "location_profiler_prompt_template",
                ),
                ("entity_miner_event_profiler", "event profiler", "event_profiler_prompt_template"),
                (
                    "entity_miner_object_profiler",
                    "object profiler",
                    "object_profiler_prompt_template",
                ),
                (
                    "entity_miner_organization_profiler",
                    "organization profiler",
                    "organization_profiler_prompt_template",
                ),
                (
                    "entity_miner_relationship_extraction",
                    "relationship extraction",
                    "relationship_extractor_prompt_template",
                ),
            ]

            for template_type, label, attr_name in templates_to_fetch:
                setattr(self, attr_name, self._fetch_template(template_type, label))

            span.set_status(Status(StatusCode.OK))

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
        with tracer.start_as_current_span("fetch_template") as span:
            span.set_attribute("template.type", template_type)
            span.set_attribute("template.label", label)

            try:
                response = self.prompt_template_table.get_item(
                    Key={"novel_name": "global", "template_type": template_type}
                )
                item = response.get("Item", {})
                if not item:
                    span.set_attribute("template.found", False)
                    logger.warning(f"{label} template not found in DynamoDB")
                else:
                    span.set_attribute("template.found", True)
                span.set_status(Status(StatusCode.OK))
                return item
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                return {}

    def invoke_model(
        self,
        model_id: str,
        system_prompt: str,
        instruction_prompt: str,
        temperature: float = 0,
        top_p: float = 0.9,
        seed: int = 69420,
    ):
        with tracer.start_as_current_span("bedrock_invoke_model") as span:
            span.set_attribute(
                "genai.system_prompt.length", len(system_prompt) if system_prompt else 0
            )
            span.set_attribute(
                "genai.instruction_prompt.length",
                len(instruction_prompt) if instruction_prompt else 0,
            )

            if not model_id or not system_prompt or not instruction_prompt:
                span.set_status(Status(StatusCode.ERROR, "Parameters missing"))
                raise ValueError("model_id, system_prompt, and instruction_prompt cannot be empty")

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

                span.set_status(Status(StatusCode.OK))
                return response
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, "Model invocation failed"))
                logger.error(f"Error invoking model: {e}")
                raise

    def _parse_response(self, response, model_output_schema: BaseModel) -> BaseModel:
        content = (
            json.loads(response.get("body").read()).get("choices")[0].get("message").get("content")
        )
        extracted_json = content.split("```json")[-1].split("```")[0]
        parsed = json.loads(extracted_json)

        if model_output_schema is EntityExtractionAndClassification and isinstance(parsed, list):
            parsed = {"entities": parsed}

        return model_output_schema.model_validate(parsed)

    @staticmethod
    def _get_prompts(template: dict, label: str) -> tuple[str, str]:
        system_prompt = template.get("system_prompt_template")
        instruction_prompt = template.get("instruction_prompt_template")
        if not system_prompt or not instruction_prompt:
            raise ValueError(f"Missing prompts for {label}")
        return system_prompt, instruction_prompt

    def extract_genre(self, text: str) -> GenreDetermination:
        with tracer.start_as_current_span("extract_genre") as span:
            system_prompt, instruction_prompt = self._get_prompts(
                self.genre_determination_prompt_template, "genre_determination"
            )
            instruction_prompt = instruction_prompt.format(text=text)
            response = self.invoke_model(
                model_id=self.model_id,
                system_prompt=system_prompt,
                instruction_prompt=instruction_prompt,
            )
            result = self._parse_response(response, GenreDetermination)
            span.set_attribute("genre.detected", result.genre)
            return result

    def extract_entities(self, text: str, genre: str) -> EntityExtractionAndClassification:
        with tracer.start_as_current_span("extract_entities") as span:
            system_prompt, instruction_prompt = self._get_prompts(
                self.entity_extraction_and_classification_prompt_template, "entity_extraction"
            )
            instruction_prompt = instruction_prompt.format(genre=genre, text=text)
            response = self.invoke_model(
                model_id=self.model_id,
                system_prompt=system_prompt,
                instruction_prompt=instruction_prompt,
            )
            result = self._parse_response(response, EntityExtractionAndClassification)
            span.set_attribute("entities.count", len(result.entities))
            return result

    def profile_entity(
        self, text: str, entity_name: str, genre: str, category: str, significance: str = None
    ) -> BaseModel:
        with tracer.start_as_current_span("profile_entity") as span:
            span.set_attribute("entity.name", entity_name)
            span.set_attribute("entity.category", category)

            if category not in self.profile_config:
                return None

            config = self.profile_config[category]
            system_prompt, instruction_prompt = self._get_prompts(
                config["template"], config["label"]
            )

            format_args = {"entity_name": entity_name, "genre": genre, "text": text}
            if category == "Person" and significance != "Minor":
                format_args["significance"] = significance

            instruction_prompt = instruction_prompt.format(**format_args)

            response = self.invoke_model(
                model_id=self.model_id,
                system_prompt=system_prompt,
                instruction_prompt=instruction_prompt,
            )
            return self._parse_response(response, config["schema"])

    def execute(self, text: str) -> dict:
        with tracer.start_as_current_span("entity_mining_execution") as span:
            genre_result = self.extract_genre(text=text)
            genre = genre_result.genre

            extracted_entities = self.extract_entities(text=text, genre=genre)

            profiled_entities = []
            failed_profiles = 0

            max_workers = self.config.get("aws").get("thread_pool_max_workers", 10)
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(
                        self.profile_entity,
                        text=text,
                        entity_name=entity.name,
                        genre=genre,
                        category=entity.category,
                        significance=(entity.significance if entity.significance else None),
                    )
                    for entity in extracted_entities.entities
                ]
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        if result:
                            profiled_entities.append(result)
                    except Exception as e:
                        failed_profiles += 1
                        logger.error(f"Error profiling entity: {e}")

            span.set_attribute("entities.profiled", len(profiled_entities))
            return {
                "genre": genre,
                "genre_determination_reasoning": genre_result.reasoning,
                "profiled_entities": profiled_entities,
            }

    def save_entities_to_chroma(
        self, entity_profiles: list[BaseModel], genre: str, novel_name: str
    ) -> bool:
        with tracer.start_as_current_span("save_to_chromadb") as span:
            try:
                doc_ids = []
                for profile in entity_profiles:
                    name = getattr(profile, "name", getattr(profile, "primary_name", "unknown"))
                    doc_ids.append(f"{novel_name}-{name}")

                self.chroma_collection.add(
                    documents=[profile.model_dump_json() for profile in entity_profiles],
                    metadatas=[
                        {
                            "novel_name": novel_name,
                            "genre": genre,
                            "source": "entity_miner",
                            "created_at": datetime.datetime.now().isoformat(),
                        }
                        for _ in entity_profiles
                    ],
                    ids=doc_ids,
                )
                return True
            except Exception as e:
                span.record_exception(e)
                logger.error(f"Error saving to ChromaDB: {e}")
                return False


def lambda_handler(event, context_obj) -> dict:
    provider = trace.get_tracer_provider()


    result = {
        "status": None,
        "error_type": None,
        "error_message": None,
        "result_timestamp": int(datetime.datetime.now().timestamp()),
    }

    try:
        with tracer.start_as_current_span("lambda_handler") as span:
            if "Records" in event and len(event.get("Records", [])) > 0:
                record = event["Records"][0]
                if record.get("eventSource") == "aws:s3":
                    bucket_name = record["s3"]["bucket"]["name"]
                    key = record["s3"]["object"]["key"]
                    config = load_config()
                    s3_client = boto3.client("s3", region_name=config.get("aws").get("region"))
                    file_object = s3_client.get_object(Bucket=bucket_name, Key=key)
                    story_text = file_object["Body"].read().decode("utf-8")
                    novel_name = key.split("/")[-1].split(".")[0]
                    username = file_object["Metadata"].get("username", "unknown")
                else:
                    raise ValueError(f"Unsupported event source: {record.get('eventSource')}")
            # asynchronous invocation from the frontend. This is the main entry point for the Lambda function.
            elif "text" in event: 
                story_text = event.get("text")
                novel_name = event.get("novel_name")
                username = event.get("username", "unknown")
            else:
                raise ValueError(f"'text' not in Lambda JSON Payload")

            span.set_attribute("novel.name", novel_name)
            span.set_attribute("username", username)
            span.set_attribute("story.text.length", len(story_text) if story_text else 0)

            entity_miner = EntityMiningWorkflow(
                novel_name=novel_name, chroma_collection_name=f"{username}-{novel_name}"
            )

            mined_entities = entity_miner.execute(story_text)
            saved = entity_miner.save_entities_to_chroma(
                mined_entities["profiled_entities"], mined_entities["genre"], novel_name
            )

            span.set_attribute("entities.mined", len(mined_entities["profiled_entities"]))
            span.set_attribute("entities.saved", saved)

            result["status"] = "SUCCESS" if saved else "FAILURE"
            return result
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        result["status"] = "FAILURE"
        result["error_type"] = "ValidationError"
        result["error_message"] = str(e)
        return result
    except Exception as e:
        logger.error(f"Unexpected error in lambda_handler: {e}", exc_info=True)
        result["status"] = "FAILURE"
        result["error_type"] = type(e).__name__
        result["error_message"] = str(e)
        return result
    finally:
        # Always flush traces, even on error
        if provider and hasattr(provider, "force_flush"):
            try:
                provider.force_flush()
            except Exception as e:
                logger.warning(f"Failed to flush traces: {e}")

# dirty but works. TODO: refactor OTel instrumentation to be more pythonic.
AwsLambdaInstrumentor().instrument()

if __name__ == "__main__":
    prologue_path = "stories/nadarr_prologue.txt"
    
    if not os.path.exists(prologue_path):
        logger.error(f"Text file not found at: {prologue_path}")
    else:
        with open(prologue_path) as f:
            text = f.read()
        
        entity_miner = EntityMiningWorkflow(
            novel_name="nadarr_prologue", 
            local_chroma=True
        )
        
        result = entity_miner.execute(text)
        logger.info(f"Execution complete. Found {len(result['profiled_entities'])} entities.")

        logger.info(f"Mined entities: {result}")

        saved = entity_miner.save_entities_to_chroma(result['profiled_entities'], result['genre'], "nadarr_prologue")
        logger.info(f"Entities saved to ChromaDB: {saved}")
        
        provider = trace.get_tracer_provider()
        if hasattr(provider, "shutdown"):
            provider.shutdown()

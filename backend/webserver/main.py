import hashlib
import json
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime

import boto3
import chromadb
from botocore.config import Config
from fastapi import FastAPI, HTTPException
from langchain_aws import ChatBedrockConverse
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel

from utils import get_template_from_dynamo, load_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Pydantic Models ---


class StoryUploadRequest(BaseModel):
    text: str
    filepath: str
    bucket_name: str
    username: str
    story_text_hash: str


class EntityAddRequest(BaseModel):
    entity: str
    description: str
    key_relations: str
    history: str


class MineEntitiesRequest(BaseModel):
    story_text: str
    novel_name: str
    username: str


class PromptTemplateResponse(BaseModel):
    novel_name: str
    template_type: str
    prompt_template: str
    date: str
    version: str


# --- Global State / Configuration ---


class AppState:
    s3_client = None
    prompt_templates_table = None
    chroma_collection = None
    llm = None
    lambda_client = None
    config = None


state = AppState()

# --- Initialization ---


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing resources...")
    try:
        state.config = load_config()
        aws_config = state.config.get("aws", {})
        region = aws_config.get("region", "ap-south-1")

        # AWS Resources
        state.s3_client = boto3.client("s3", region_name=region)

        lambda_client_config = Config(
            connect_timeout=10, read_timeout=600, retries={"max_attempts": 2}
        )

        state.lambda_client = boto3.client(
            "lambda", region_name=region, config=lambda_client_config
        )
        dynamodb = boto3.resource("dynamodb", region_name=region)
        state.prompt_templates_table = dynamodb.Table(
            state.config.get("aws").get("dynamodb_table")
        )
        state.job_records_table = dynamodb.Table(
            state.config.get("aws").get("jobs_table")
        )

        # ChromaDB
        try:
            chroma_client = chromadb.HttpClient(
                host=state.config.get("chroma").get("remote").get("host"),
                port=state.config.get("chroma").get("remote").get("port"),
            )
            state.chroma_collection = chroma_client.get_or_create_collection(
                name=state.config.get("chroma").get("default_collection")
            )
            logger.info(
                f"ChromaDB collection '{state.config.get('chroma').get('default_collection')}' created or retrieved successfully."
            )
        except Exception as e:
            logger.warning(
                f"Could not connect to ChromaDB: {e}. Vector search features will fail."
            )

        state.llm = ChatBedrockConverse(
            model_id=state.config.get("aws")
            .get("story_completion_llm")
            .get("model_id"),
            region_name=region,
            temperature=state.config.get("aws")
            .get("story_completion_llm")
            .get("temperature"),
        )

        logger.info("Resources initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize resources: {e}")
        raise

    yield


app = FastAPI(lifespan=lifespan, title="NovelWriter API")

# --- Endpoints ---


@app.get("/api/story")
async def get_story(bucket: str, object_key: str):
    """Fetches a story object from an S3 bucket."""
    try:
        response = state.s3_client.get_object(Bucket=bucket, Key=object_key)
        content = response["Body"].read().decode("utf-8")
        return {"content": content}
    except state.s3_client.exceptions.NoSuchKey:
        raise HTTPException(
            status_code=404,
            detail=f"Object '{object_key}' not found in bucket '{bucket}'",
        )
    except Exception as e:
        logger.error(f"S3 Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/story")
async def upload_story(request: StoryUploadRequest):
    """Uploads a story object to an S3 bucket."""
    story_text_hash = hashlib.sha256(request.text.encode("utf-8")).hexdigest()
    try:
        state.s3_client.put_object(
            Bucket=request.bucket_name,
            Key=request.filepath,
            Body=request.text,
            ContentType="plain/text",
            Metadata={"username": request.username, "story_text_hash": story_text_hash},
        )
        return {"message": "Story uploaded successfully", "path": request.filepath}
    except Exception as e:
        logger.error(f"S3 Upload Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/templates")
async def get_prompt_template(novel_name: str, template_type: str):
    """Fetches prompt templates from DynamoDB."""
    try:
        item = state.prompt_templates_table.get_item(
            Key={"novel_name": novel_name, "template_type": template_type}
        )
        if not item.get("Item"):
            raise HTTPException(
                status_code=404, detail=f"Template not found for {template_type}"
            )
        return item.get("Item")
    except Exception as e:
        logger.error(f"DynamoDB Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/similar_entities")
async def get_similar_entities(query_text: str, n_results: int = 3):
    """Retrieves similar entity vectors from ChromaDB."""
    if not state.chroma_collection:
        raise HTTPException(status_code=503, detail="ChromaDB service unavailable")

    try:
        results = state.chroma_collection.query(
            query_texts=[query_text], n_results=n_results
        )

        entities = []
        if results and results["documents"]:
            for i in range(len(results["documents"][0])):
                entities.append(
                    {
                        "content": results["documents"][0][i],
                        "metadata": (
                            results["metadatas"][0][i] if results["metadatas"] else {}
                        ),
                        "distance": (
                            results["distances"][0][i] if results["distances"] else None
                        ),
                    }
                )
        return {"entities": entities}
    except Exception as e:
        logger.error(f"ChromaDB Query Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/entity")
async def add_entity(request: EntityAddRequest):
    """Adds an entity manually to the ChromaDB."""
    if not state.chroma_collection:
        raise HTTPException(status_code=503, detail="ChromaDB service unavailable")

    try:
        document_text = f"{request.entity}: {request.description}\nRelations: {request.key_relations}\nHistory: {request.history}"

        # TODO: Change to use a more robust ID generation strategy
        doc_id = f"{request.entity}-{datetime.now().timestamp()}"

        state.chroma_collection.add(
            documents=[document_text],
            metadatas=[{"source": "manual_entry", "entity": request.entity}],
            ids=[doc_id],
        )
        return {"message": "Entity added successfully", "id": doc_id}
    except Exception as e:
        logger.error(f"ChromaDB Add Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/start_entity_mining")
async def start_entity_mining(request: MineEntitiesRequest):
    """Mines entities from story text using the entity-miner Lambda function.

    Adds a job record to the DynamoDB table with the status "RUNNING".
    Calls a Step Functions state machine to invoke the Lambda function asynchronously.
    """
    if not state.lambda_client:
        raise HTTPException(status_code=503, detail="Lambda service unavailable")

    job_id = str(uuid.uuid4())
    created_at = int(datetime.now().timestamp())
    put_job_record_response = state.job_records_table.put_item(
        Item={
            "job_id": job_id,
            "user_id": request.username,
            "status": "RUNNING",
            "created_at": created_at,
            "input_type": "TEXT",
        }
    )
    if put_job_record_response.get("ResponseMetadata").get("HTTPStatusCode") != 200:
        raise HTTPException(
            status_code=500, detail="Failed to add job record to DynamoDB"
        )

    invoke_lambda_response = state.lambda_client.invoke(
        FunctionName="entity-miner",
        InvocationType="Event",
        Payload=json.dumps(
            {
                "text": request.story_text,
                "novel_name": request.novel_name,
                "username": request.username,
            }
        ),
    )
    if invoke_lambda_response.get("ResponseMetadata").get("HTTPStatusCode") != 202:
        raise HTTPException(status_code=500, detail="Failed to invoke Lambda function")

    return {
        "job_id": job_id,
        "created_at": created_at,
        "status": "RUNNING",
    }


@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    response = state.job_records_table.get_item(Key={"job_id": job_id})
    if not response.get("Item"):
        raise HTTPException(status_code=404, detail="Job not found")
    return response.get("Item")


@app.get("/api/generate")
async def generate_story(bucket: str, story_key: str, novel_name: str = "first novel"):
    """
    Generates a story continuation.
    1. Fetches current story from S3.
    2. Retrieves templates (Forecaster & Completion).
    3. Runs Forecaster chain (Vector Search + LLM).
    4. Runs Completion chain (LLM).
    """
    if not state.llm:
        raise HTTPException(status_code=503, detail="LLM service unavailable")

    # 1. Fetch Story
    try:
        s3_response = state.s3_client.get_object(Bucket=bucket, Key=story_key)
        story_content = s3_response["Body"].read().decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not fetch story: {e}")

    # 2. Prepare Text Splitter & Docs
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2048,
        chunk_overlap=256,
        length_function=len,
        is_separator_regex=False,
    )
    docs = text_splitter.create_documents([story_content])
    if not docs:
        raise HTTPException(
            status_code=400, detail="Story content is empty or could not be split."
        )

    current_fragment = docs[-1].page_content
    context_fragment = (
        "\n".join([doc.page_content for doc in docs[:-3]]) if len(docs) > 3 else ""
    )

    # 3. Fetch Templates
    try:
        forecaster_data = get_template_from_dynamo(novel_name, "forecaster")
        completion_data = get_template_from_dynamo(novel_name, "novel_completion")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch templates: {e}")

    forecaster_prompt = PromptTemplate.from_template(forecaster_data["prompt_template"])
    completion_prompt = PromptTemplate.from_template(completion_data["prompt_template"])

    # 4. Run Forecaster
    # Vector Search for context
    vector_search_results = ""
    if state.chroma_collection:
        try:
            results = state.chroma_collection.query(
                query_texts=[current_fragment], n_results=3
            )
            if results and results["documents"]:
                vector_search_results = "\n".join(results["documents"][0])
        except Exception as e:
            logger.warning(f"Vector search failed during generation: {e}")

    forecaster_chain = forecaster_prompt | state.llm | StrOutputParser()

    try:
        forecaster_response = forecaster_chain.invoke(
            {
                "vector_search_results": vector_search_results,
                "current_story_fragment": current_fragment,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecaster chain failed: {e}")

    # 5. Run Completion
    completion_chain = completion_prompt | state.llm | StrOutputParser()

    try:
        completion_response = completion_chain.invoke(
            {
                "current_story_fragment": context_fragment,
                "forecaster_response": forecaster_response,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Completion chain failed: {e}")

    return {
        "forecaster_response": forecaster_response,
        "story_continuation": completion_response,
    }

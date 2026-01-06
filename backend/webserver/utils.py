import logging
import json

logger = logging.getLogger(__name__)


def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("config.json not found.")
        raise
    except json.JSONDecodeError:
        logger.error("Error decoding config.json.")
        raise


def get_template_from_dynamo(novel_name: str, template_type: str) -> dict:
    config = load_config()
    try:
        response = (
            config.get("aws")
            .get("dynamodb_table")
            .get_item(Key={"novel_name": novel_name, "template_type": template_type})
        )
        item = response.get("Item")
        if not item:
            raise ValueError(f"Template not found for {novel_name} - {template_type}")
        return item
    except Exception as e:
        logger.error(f"DynamoDB Error: {e}")
        raise


def add_job_record_to_dynamo(
    job_id: str,
    user_id: str,
    status: str,
    created_at: int,
    input_type: str,
    error_message: str = None,
    updated_at: int = None,
) -> None:
    config = load_config()
    try:
        response = (
            config.get("aws")
            .get("jobs_table")
            .put_item(
                Item={
                    "job_id": job_id,
                    "user_id": user_id,
                    "status": status,
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "input_type": input_type,
                    "error_message": error_message,
                }
            )
        )
        return response
    except Exception as e:
        logger.error(f"DynamoDB Error: {e}")
        raise


# def update_job_record_in_dynamo(job_id: str, created_at: int = None):
#     config = load_config()
#     try:
#         response = (
#             config.get("aws")
#             .get("jobs_table")
#             .update_item(
                
#             )
#         )
#     except Exception as e:
#         logger.error(f"DynamoDB Error: {e}")
#     pass
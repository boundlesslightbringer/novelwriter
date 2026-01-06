resource "aws_sfn_state_machine" "entity_mining_state_machine" {
  name     = "entity-mining-state-machine"
  role_arn = aws_iam_role.entity_mining_state_machine_role.arn
  definition = jsonencode({
    "StartAt": "InvokeEntityMiner",
    "States": {
      "InvokeEntityMiner": {
        "Type": "Task",
        "Resource": "arn:aws:states:::lambda:invoke",
        "Parameters": {
          "FunctionName": "${aws_lambda_function.entity-miner.arn}",
          "Payload.$": "$"
        },
        "ResultPath": "$.result",
        "TimeoutSeconds": 900,
        "Retry": [
          {
            "ErrorEquals": [
              "Lambda.ServiceException",
              "Lambda.AWSLambdaException",
              "Lambda.SdkClientException",
              "Lambda.TooManyRequestsException"
            ],
            "IntervalSeconds": 1,
            "MaxAttempts": 3,
            "BackoffRate": 2,
            "JitterStrategy": "FULL"
          }
        ],
        "Next": "CheckEntityMinerResult"
      },
      "CheckEntityMinerResult": {
        "Type": "Choice",
        "Choices": [
          {
            "Variable": "$.result.Payload.status",
            "StringEquals": "SUCCESS",
            "Next": "UpdateEntityMiningJobSuccess"
          }
        ],
        "Default": "UpdateEntityMiningJobFailed"
      },
      "UpdateEntityMiningJobSuccess": {
        "Type": "Task",
        "Resource": "arn:aws:states:::dynamodb:updateItem",
        "Parameters": {
          "TableName": "${aws_dynamodb_table.job_records.name}",
          "Key": {
            "job_id": {
              "S.$": "$.job_id"
            },
            "created_at": {
              "N.$": "$.created_at"
            }
          },
          "UpdateExpression": "SET #status = :new_status, #updated_at = :new_updated_at",
          "ExpressionAttributeNames": {
            "#status": "status",
            "#updated_at": "updated_at"
          },
          "ExpressionAttributeValues": {
            ":new_status": {
              "S": "DONE"
            },
            ":new_updated_at": {
              "N.$": "$.result.Payload.result_timestamp"
            }
          },
          "ReturnValues": "UPDATED_NEW"
        },
        "End": true
      },
      "UpdateEntityMiningJobFailed": {
        "Type": "Task",
        "Resource": "arn:aws:states:::dynamodb:updateItem",
        "Parameters": {
          "TableName": "${aws_dynamodb_table.job_records.name}",
          "Key": {
            "job_id": {
              "S.$": "$.job_id"
            },
            "created_at": {
              "N.$": "$.created_at"
            }
          },
          "UpdateExpression": "SET #status = :new_status, #updated_at = :new_updated_at, #error_message = :error_message",
          "ExpressionAttributeNames": {
            "#status": "status",
            "#updated_at": "updated_at",
            "#error_message": "error_message"
          },
          "ExpressionAttributeValues": {
            ":new_status": {
              "S": "FAILED"
            },
            ":new_updated_at": {
              "N.$": "$.result.Payload.result_timestamp"
            },
            ":error_message": {
              "S.$": "$.result.Payload.error_message"
            }
          },
          "ReturnValues": "UPDATED_NEW"
        },
        "End": true
      }
    }
  })
}
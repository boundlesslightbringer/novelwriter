# This file is for defining output variables.
# Outputs are values that are displayed to the user when Terraform applies the configuration.

output "chroma_server_private_ip" {
  description = "Private IP address of the Chroma server"
  value       = aws_instance.chroma_server.private_ip
}

output "react_server_private_ip" {
  description = "Private IP address of the React server"
  value       = aws_instance.react-server.private_ip
}

output "chroma_endpoint" {
  description = "Chroma database endpoint URL"
  value       = "http://${aws_instance.chroma_server.private_ip}:8000"
}

output "s3_bucket_name" {
  description = "S3 bucket name for stories"
  value       = aws_s3_bucket.stories.id
}

output "dynamodb_table_name" {
  description = "DynamoDB table name for prompt templates"
  value       = aws_dynamodb_table.prompt_templates.name
}

output "lambda_function_name" {
  description = "Entity miner Lambda function name"
  value       = aws_lambda_function.entity-miner.function_name
}
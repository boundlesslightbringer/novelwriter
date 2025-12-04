# This file is for defining output variables.
# Outputs are values that are displayed to the user when Terraform applies the configuration.

output "chroma_server_private_ip" {
  description = "Private IP address of the Chroma server"
  value       = aws_instance.chroma_server.private_ip
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

output "ecs_cluster_name" {
  description = "Name of the ECS cluster hosting frontend and backend services"
  value       = aws_ecs_cluster.novelwriter.name
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster hosting frontend and backend services"
  value       = aws_ecs_cluster.novelwriter.arn
}

output "frontend_service_name" {
  description = "ECS service name for the frontend"
  value       = aws_ecs_service.frontend.name
}

output "backend_service_name" {
  description = "ECS service name for the backend"
  value       = aws_ecs_service.backend.name
}
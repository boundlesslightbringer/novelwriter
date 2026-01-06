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

output "fastapi_server_private_ip" {
  description = "Private IP address of the FastAPI backend server"
  value       = aws_instance.fastapi-server.private_ip
}

output "chroma_endpoint" {
  description = "Chroma database endpoint URL"
  value       = "http://${aws_instance.chroma_server.private_ip}:8000"
}

output "s3_bucket_name" {
  description = "S3 bucket name for stories"
  value       = aws_s3_bucket.stories.id
}

output "dynamodb_prompt_templates_table_name" {
  description = "DynamoDB table name for prompt templates"
  value       = aws_dynamodb_table.prompt_templates.name
}

output "dynamodb_job_records_table_name" {
  description = "DynamoDB table name for job records"
  value       = aws_dynamodb_table.job_records.name
}

output "lambda_function_name" {
  description = "Entity miner Lambda function name"
  value       = aws_lambda_function.entity-miner.function_name
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.webapp.dns_name
}

output "alb_url" {
  description = "Full URL to access the application"
  value       = "http://${aws_lb.webapp.dns_name}"
}
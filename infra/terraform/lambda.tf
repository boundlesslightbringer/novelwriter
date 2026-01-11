resource "aws_lambda_function" "entity-miner" {
  function_name    = "entity-miner"
  role             = aws_iam_role.entity_miner_lambda_role.arn
  package_type =  "Image"
  image_uri = "066777916969.dkr.ecr.ap-south-1.amazonaws.com/primary@sha256:ca588582f16fbf841cec147674bd15e5856ec05b7fc947ea1df0735c587199a1"
  timeout      = 420 # 7 minutes
  memory_size  = 1024 # 1 GB

  vpc_config {
    subnet_ids         = [aws_subnet.private.id]
    security_group_ids = [aws_security_group.backend.id]
  }

  environment {
    variables = {
      OTEL_SERVICE_NAME = "entity-miner"
      OTEL_LOG_LEVEL = "info"
      OTEL_EXPORTER_OTLP_PROTOCOL = "http/protobuf"
      OTEL_EXPORTER_OTLP_ENDPOINT = "${aws_instance.fastapi-server.private_ip}:4318"
    }
  }
} 

resource "aws_lambda_function_event_invoke_config" "entity-miner-s3-file-modified" {
  function_name = aws_lambda_function.entity-miner.function_name
  maximum_retry_attempts = 1
  maximum_event_age_in_seconds = 3600
  qualifier = "$LATEST"
}
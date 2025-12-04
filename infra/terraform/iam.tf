resource "aws_iam_role" "entity_miner_lambda_role" {
  name = "entity-miner-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.entity_miner_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_vpc_access" {
  role       = aws_iam_role.entity_miner_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# Policy to allow Lambda to read from S3
resource "aws_iam_policy" "lambda_s3_read" {
  name        = "lambda-s3-read-policy"
  description = "Allows Lambda to read from S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Effect = "Allow"
        Resource = [
          aws_s3_bucket.stories.arn,
          "${aws_s3_bucket.stories.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_s3_access" {
  role       = aws_iam_role.entity_miner_lambda_role.name
  policy_arn = aws_iam_policy.lambda_s3_read.arn
}

resource "aws_iam_role" "react_server_role" {
  name = "react-server-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "bedrock_access" {
  name        = "bedrock-access-policy"
  description = "Allows access to Bedrock"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "bedrock:InvokeModel",
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "react_server_bedrock_access" {
  role       = aws_iam_role.react_server_role.name
  policy_arn = aws_iam_policy.bedrock_access.arn
}

# Policy to allow react server to access S3
resource "aws_iam_policy" "react_server_s3_access" {
  name        = "react-server-s3-access-policy"
  description = "Allows react server to access S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Effect = "Allow"
        Resource = [
          aws_s3_bucket.stories.arn,
          "${aws_s3_bucket.stories.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "react_server_s3_access" {
  role       = aws_iam_role.react_server_role.name
  policy_arn = aws_iam_policy.react_server_s3_access.arn
}

# Policy to allow react server to access DynamoDB
resource "aws_iam_policy" "react_server_dynamodb_access" {
  name        = "react-server-dynamodb-access-policy"
  description = "Allows react server to access DynamoDB"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Effect = "Allow"
        Resource = [
          aws_dynamodb_table.prompt_templates.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "react_server_dynamodb_access" {
  role       = aws_iam_role.react_server_role.name
  policy_arn = aws_iam_policy.react_server_dynamodb_access.arn
}

resource "aws_iam_policy" "react_server_ecr_access" {
  name        = "react-server-ecr-access-policy"
  description = "Allows React server to pull images from ECR"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "react_server_ecr_access" {
  role       = aws_iam_role.react_server_role.name
  policy_arn = aws_iam_policy.react_server_ecr_access.arn
}

resource "aws_iam_instance_profile" "react_server_profile" {
  name = "react-server-profile"
  role = aws_iam_role.react_server_role.name
}

# FastAPI Backend Server IAM Role and Policies
resource "aws_iam_role" "fastapi_server_role" {
  name = "fastapi-server-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "fastapi_server_bedrock_access" {
  role       = aws_iam_role.fastapi_server_role.name
  policy_arn = aws_iam_policy.bedrock_access.arn
}

resource "aws_iam_policy" "fastapi_server_s3_access" {
  name        = "fastapi-server-s3-access-policy"
  description = "Allows FastAPI server to access S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Effect = "Allow"
        Resource = [
          aws_s3_bucket.stories.arn,
          "${aws_s3_bucket.stories.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "fastapi_server_s3_access" {
  role       = aws_iam_role.fastapi_server_role.name
  policy_arn = aws_iam_policy.fastapi_server_s3_access.arn
}

resource "aws_iam_policy" "fastapi_server_dynamodb_access" {
  name        = "fastapi-server-dynamodb-access-policy"
  description = "Allows FastAPI server to access DynamoDB"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Effect = "Allow"
        Resource = [
          aws_dynamodb_table.prompt_templates.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "fastapi_server_dynamodb_access" {
  role       = aws_iam_role.fastapi_server_role.name
  policy_arn = aws_iam_policy.fastapi_server_dynamodb_access.arn
}

resource "aws_iam_policy" "fastapi_server_ecr_access" {
  name        = "fastapi-server-ecr-access-policy"
  description = "Allows FastAPI server to pull images from ECR"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "fastapi_server_ecr_access" {
  role       = aws_iam_role.fastapi_server_role.name
  policy_arn = aws_iam_policy.fastapi_server_ecr_access.arn
}

resource "aws_iam_instance_profile" "fastapi_server_profile" {
  name = "fastapi-server-profile"
  role = aws_iam_role.fastapi_server_role.name
}
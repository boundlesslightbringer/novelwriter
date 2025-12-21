
data "aws_ami" "amazon-linux-2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# react application server
resource "aws_instance" "react-server" {
  ami                         = data.aws_ami.amazon-linux-2.id
  instance_type               = "t3.micro"
  subnet_id                   = aws_subnet.public.id
  key_name                    = data.aws_key_pair.react-server-ed25519.key_name
  vpc_security_group_ids      = [aws_security_group.frontend.id]
  iam_instance_profile        = aws_iam_instance_profile.react_server_profile.name
  associate_public_ip_address = true

  user_data = <<-EOF
    #!/bin/bash
    # Update system and install dependencies
    sudo yum update -y
    sudo yum install -y docker aws-cli
    
    # Start Docker service
    sudo systemctl enable docker
    sudo systemctl start docker
    sudo usermod -a -G docker ec2-user
    
    # Authenticate with ECR
    aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 066777916969.dkr.ecr.ap-south-1.amazonaws.com
    
    # Pull the React frontend image from ECR
    docker pull 066777916969.dkr.ecr.ap-south-1.amazonaws.com/primary:frontend-latest
    
    # Run the React frontend container
    docker run -d \
      --name react-frontend \
      --restart unless-stopped \
      -p 80:80 \
      066777916969.dkr.ecr.ap-south-1.amazonaws.com/primary:frontend-latest
      EOF

  cpu_options {
    core_count       = 1
    threads_per_core = 2
  }

  tags = {
    Name = "react-server"
  }

  depends_on = [aws_instance.fastapi-server]
}

# FastAPI backend server
resource "aws_instance" "fastapi-server" {
  ami                         = data.aws_ami.amazon-linux-2.id
  instance_type               = "t3.micro"
  subnet_id                   = aws_subnet.private.id
  key_name                    = data.aws_key_pair.fastapi-server-ed25519.key_name
  vpc_security_group_ids      = [aws_security_group.backend.id]
  iam_instance_profile        = aws_iam_instance_profile.fastapi_server_profile.name
  associate_public_ip_address = false

  user_data = <<-EOF
    #!/bin/bash
    # Update system and install dependencies
    sudo yum update -y
    sudo yum install -y docker aws-cli
    
    # Start Docker service
    sudo systemctl enable docker
    sudo systemctl start docker
    sudo usermod -a -G docker ec2-user
    
    # Authenticate with ECR
    aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 066777916969.dkr.ecr.ap-south-1.amazonaws.com
    
    # Pull the FastAPI backend image from ECR
    docker pull 066777916969.dkr.ecr.ap-south-1.amazonaws.com/primary:novelwriter-webserver-latest
    
    # Run the FastAPI backend container
    docker run -d \
      --name fastapi-backend \
      --restart unless-stopped \
      -p 7000:7000 \
      066777916969.dkr.ecr.ap-south-1.amazonaws.com/primary:novelwriter-webserver-latest
      EOF

  cpu_options {
    core_count       = 1
    threads_per_core = 2
  }

  tags = {
    Name = "fastapi-server"
  }

  depends_on = [aws_instance.chroma_server]
}

resource "aws_lambda_function" "entity-miner" {
  function_name    = "entity-miner"
  role             = aws_iam_role.entity_miner_lambda_role.arn
  package_type =  "Image"
  image_uri = "066777916969.dkr.ecr.ap-south-1.amazonaws.com/primary@sha256:2c18b0ccdf7adea44faa7ec62589bf779f5af569610a5746b8d1bf065cb73e26"
  timeout      = 420 # 7 minutes
  memory_size  = 1024 # 1 GB

  vpc_config {
    subnet_ids         = [aws_subnet.private.id]
    security_group_ids = [aws_security_group.backend.id]
  }
} 

resource "aws_lambda_function_event_invoke_config" "entity-miner-s3-file-modified" {
  function_name = aws_lambda_function.entity-miner.function_name
  maximum_retry_attempts = 1
  maximum_event_age_in_seconds = 3600
  qualifier = "$LATEST"
}

resource "aws_lambda_permission" "allow_s3_to_invoke_entity-miner" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.entity-miner.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.stories.arn
}
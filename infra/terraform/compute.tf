
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
  instance_type               = "t3.small"
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
}

# entity mining VM
data "archive_file" "entity_miner_zip" {
  type        = "zip"
  source_file = "${path.module}/../../backend/lambda/entity_miner.py"
  output_path = "${path.module}/../../backend/  lambda/entity_miner.zip"
}

# FastAPI backend server
resource "aws_instance" "fastapi-server" {
  ami                         = data.aws_ami.amazon-linux-2.id
  instance_type               = "t3.small"
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
}

resource "aws_lambda_function" "entity-miner" {
  function_name    = "entity-miner"
  role             = aws_iam_role.entity_miner_lambda_role.arn
  handler          = "entity_miner.lambda_handler"
  runtime          = "python3.9"
  filename         = data.archive_file.entity_miner_zip.output_path
  source_code_hash = data.archive_file.entity_miner_zip.output_base64sha256

  vpc_config {
    subnet_ids         = [aws_subnet.private.id]
    security_group_ids = [aws_security_group.backend.id]
  }
}

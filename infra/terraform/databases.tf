data "aws_ami" "amazon-linux-2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# chromadb server
resource "aws_instance" "chroma_server" {
  ami                         = data.aws_ami.amazon-linux-2.id
  instance_type               = "t3.small"
  subnet_id                   = aws_subnet.private.id
  key_name                    = data.aws_key_pair.chroma-server-ed25519.key_name
  vpc_security_group_ids      = [aws_security_group.application.id]
  associate_public_ip_address = false

  user_data = <<-EOF
    #!/bin/bash
    amazon-linux-extras install docker -y
    usermod -a -G docker ec2-user
    curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
    systemctl enable docker
    systemctl start docker

    mkdir -p /home/ec2-user/config
    curl -o /home/ec2-user/docker-compose.yml https://s3.amazonaws.com/public.trychroma.com/cloudformation/assets/docker-compose.yml
    sed -i 's/CHROMA_VERSION/${var.chroma_version}/g' /home/ec2-user/docker-compose.yml
    chown ec2-user:ec2-user /home/ec2-user/docker-compose.yml
    
    # Create .env file with configuration
    echo 'CHROMA_SERVER_AUTHN_CREDENTIALS=${var.chroma_server_auth_credentials}' >> /home/ec2-user/.env
    echo 'CHROMA_SERVER_AUTHN_PROVIDER=${var.chroma_server_auth_provider}' >> /home/ec2-user/.env
    echo 'CHROMA_AUTH_TOKEN_TRANSPORT_HEADER=' >> /home/ec2-user/.env
    echo 'CHROMA_OTEL_COLLECTION_ENDPOINT=' >> /home/ec2-user/.env
    echo 'CHROMA_OTEL_SERVICE_NAME=' >> /home/ec2-user/.env
    echo 'CHROMA_OTEL_COLLECTION_HEADERS={}' >> /home/ec2-user/.env
    echo 'CHROMA_OTEL_GRANULARITY=' >> /home/ec2-user/.env
    chown ec2-user:ec2-user /home/ec2-user/.env
    
    cd /home/ec2-user
    sudo -u ec2-user docker-compose up -d
  EOF

  tags = {
    Name = "chroma-server"
  }

  root_block_device {
    volume_size = 24
    volume_type = "gp2"
  }

  # Ensure security group is created first
  depends_on = [aws_security_group_rule.app_to_chroma]
}

# dynamo db
resource "aws_dynamodb_table" "prompt_templates" {
  name         = "PromptTemplates"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "novel_name"
  range_key    = "template_type"

  attribute {
    name = "novel_name"
    type = "S"
  }

  attribute {
    name = "template_type"
    type = "S"
  }

  tags = {
    Name = "PromptTemplates"
  }
}
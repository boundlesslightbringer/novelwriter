
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
    # install and start the react server
    sudo yum update -y
    sudo yum install -y nginx certbot python3-certbot-nginx docker
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
  source_file = "${path.module}/../lambda/entity_miner.py"
  output_path = "${path.module}/../lambda/entity_miner.zip"
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

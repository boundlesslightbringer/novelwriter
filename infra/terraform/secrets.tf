data "aws_secretsmanager_secret_version" "docdb-primary-password" {
  secret_id = var.docdb-primary-password
}

data "aws_key_pair" "react-server-ed25519" {
  key_name = var.react-server-ed22519-kp
  include_public_key = true
}

data "aws_key_pair" "chroma-server-ed25519" {
  key_name = var.chroma-server-ed22519-kp
  include_public_key = true
}

data "aws_key_pair" "fastapi-server-ed25519" {
  key_name = var.fastapi-server-ed25519-kp
  include_public_key = true
}
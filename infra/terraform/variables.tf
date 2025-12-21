variable "aws-region" {
  description = "The AWS region to create resources in."
  type        = string
  default     = "ap-south-1"
}

variable "react-server-ed22519-kp" {
  description = ""
  type        = string
  default     = "react-server-ed25519-25112025"
}

variable "chroma-server-ed22519-kp" {
  description = ""
  type        = string
  default     = "chroma-server-ed25519-26112025"
}

variable "fastapi-server-ed25519-kp" {
  description = ""
  type        = string
  default     = "fastapi-server-ed25519-04122025"
}

variable "docdb-primary-password" {
  description = ""
  type        = string
  default     = "docdb-master-password"
}

variable "aws_access_key" {
  description = "AWS Access Key ID"
  type        = string
  sensitive   = true
}

variable "aws_secret_key" {
  description = "AWS Secret Access Key"
  type        = string
  sensitive   = true
}

variable "docdb_master_username" {
  description = ""
  type        = string
  sensitive   = false
  default     = "docdbadmin"
}

variable "chroma_version" {
  description = "Version of Chroma to deploy"
  type        = string
  default     = "1.3.6" # same as pyproject.toml
}

variable "chroma_server_auth_credentials" {
  description = "Chroma authentication credentials (leave empty for no auth)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "chroma_server_auth_provider" {
  description = "Chroma authentication provider"
  type        = string
  default     = ""
  validation {
    condition     = contains(["", "chromadb.auth.token_authn.TokenAuthenticationServerProvider", "chromadb.auth.basic_authn.BasicAuthenticationServerProvider"], var.chroma_server_auth_provider)
    error_message = "Must be empty or a valid Chroma auth provider."
  }
}

variable "LOCAL_PUBLIC_IP" {
  type        = string
  description = "My local public IP address"
}
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
  type = string
  sensitive = false
  default = "docdbadmin"
}

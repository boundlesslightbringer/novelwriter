# This is the main Terraform configuration file.
# Define your AWS resources here.

# Example resource:
# resource "aws_instance" "example" {
#   ami           = "ami-0c55b159cbfafe1f0"
#   instance_type = "t2.micro"
# }

resource "aws_ecr_repository" "primary" {
  name                 = "primary"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}
# This file is used to bootstrap the global infrastructure.
# It creates the necessary S3 bucket and DynamoDB table for the Terraform state.
# WARNING: This file should not be modified or deleted.

variable "region" {
  type        = string
  description = "The AWS region to deploy to"
}

variable "aws_profile" {
  type        = string
  description = "The AWS profile to use"
}

locals {
  tags = {
    Environment = "bootstrap"
    Project     = "Weavens"
    ManagedBy   = "Terraform"
  }
}

provider "aws" {
  region  = var.region
  profile = var.aws_profile
}

module "bootstrap" {
  source = "trussworks/bootstrap/aws"

  region        = var.region
  account_alias = "weavens"

  log_bucket_tags     = local.tags
  dynamodb_table_tags = local.tags
}

output "terraform_state_bucket_name" {
  value       = module.bootstrap.state_bucket
  description = "The name of the Terraform state bucket"
}

output "terraform_state_dynamodb_table_name" {
  value       = module.bootstrap.dynamodb_table
  description = "The name of the Terraform state DynamoDB table"
}

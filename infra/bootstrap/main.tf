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

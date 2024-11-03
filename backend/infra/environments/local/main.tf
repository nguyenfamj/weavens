terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}


provider "aws" {
  region                      = "eu-north-1"
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true
  skip_region_validation      = true

  endpoints {
    dynamodb = "http://localhost:8000"
  }
}

module "dynamodb" {
  source          = "../../modules/dynamodb"
  enable_tags     = false
  tag_environment = "local"
}

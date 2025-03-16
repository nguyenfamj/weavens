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
  source = "../../modules/dynamodb-tables"

  properties_table_config = {
    billing_mode                   = "PAY_PER_REQUEST"
    point_in_time_recovery_enabled = true
    server_side_encryption_enabled = true
  }

  checkpoints_table_config = {
    billing_mode                   = "PAY_PER_REQUEST"
    point_in_time_recovery_enabled = true
    server_side_encryption_enabled = true
  }

  scrape_jobs_table_config = {
    billing_mode                   = "PAY_PER_REQUEST"
    server_side_encryption_enabled = false
    point_in_time_recovery_enabled = false
  }

  scraped_content_table_config = {
    billing_mode                   = "PAY_PER_REQUEST"
    server_side_encryption_enabled = false
    point_in_time_recovery_enabled = false
  }

  user_message_logs_table_config = {
    billing_mode                   = "PAY_PER_REQUEST"
    server_side_encryption_enabled = false
    point_in_time_recovery_enabled = false
  }

  environment = "local"
  tags        = {}
}

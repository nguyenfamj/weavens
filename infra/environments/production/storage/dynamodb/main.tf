variable "environment" {
  type        = string
  description = "The environment to deploy to"
}

variable "tags" {
  type        = map(string)
  description = "The tags to apply to the dynamodb tables"
}

module "dynamodb_tables" {
  source = "../../../../modules/dynamodb-tables"

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

  environment = var.environment
  tags        = var.tags
}

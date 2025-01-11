module "properties" {
  source = "terraform-aws-modules/dynamodb-table/aws"

  name     = "Properties"
  hash_key = "id"

  billing_mode   = try(var.properties_table_config.billing_mode, "PAY_PER_REQUEST")
  read_capacity  = try(var.properties_table_config.read_capacity, null)
  write_capacity = try(var.properties_table_config.write_capacity, null)

  server_side_encryption_enabled = try(var.properties_table_config.server_side_encryption_enabled, false)
  point_in_time_recovery_enabled = try(var.properties_table_config.point_in_time_recovery_enabled, true)


  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  attributes = [
    { name = "id", type = "N" },
    { name = "crawled", type = "N" },
    { name = "opensearch_version", type = "N" }
  ]

  global_secondary_indexes = [
    {
      name               = "CrawledUrlGSI"
      hash_key           = "crawled"
      projection_type    = "INCLUDE"
      non_key_attributes = ["url"]
      read_capacity      = try(var.properties_table_config.crawled_url_gsi_config.read_capacity, null)
      write_capacity     = try(var.properties_table_config.crawled_url_gsi_config.write_capacity, null)
    },
    {
      name               = "IndexedOpensearchGSI"
      hash_key           = "opensearch_version"
      projection_type    = "INCLUDE"
      non_key_attributes = ["url"]
      read_capacity      = try(var.properties_table_config.indexed_opensearch_gsi_config.read_capacity, null)
      write_capacity     = try(var.properties_table_config.indexed_opensearch_gsi_config.write_capacity, null)
    }
  ]

  tags = merge(
    {
      DynamoDBTable = "properties-${var.environment}"
    },
    var.tags
  )
}

module "checkpoints" {
  source = "terraform-aws-modules/dynamodb-table/aws"

  name      = "Checkpoints"
  hash_key  = "PK"
  range_key = "SK"

  billing_mode   = try(var.checkpoints_table_config.billing_mode, "PAY_PER_REQUEST")
  read_capacity  = try(var.checkpoints_table_config.read_capacity, null)
  write_capacity = try(var.checkpoints_table_config.write_capacity, null)

  server_side_encryption_enabled = try(var.checkpoints_table_config.server_side_encryption_enabled, false)
  point_in_time_recovery_enabled = try(var.checkpoints_table_config.point_in_time_recovery_enabled, false)

  attributes = [
    { name = "PK", type = "S" },
    { name = "SK", type = "S" }
  ]

  tags = merge(
    {
      DynamoDBTable = "checkpoints-${var.environment}"
    },
    var.tags
  )
}

module "scrape_jobs_table" {
  source = "terraform-aws-modules/dynamodb-table/aws"

  name     = "ScrapeJobs"
  hash_key = "id"

  billing_mode   = try(var.scrape_jobs_table_config.billing_mode, "PAY_PER_REQUEST")
  read_capacity  = try(var.scrape_jobs_table_config.read_capacity, null)
  write_capacity = try(var.scrape_jobs_table_config.write_capacity, null)

  server_side_encryption_enabled = try(var.scrape_jobs_table_config.server_side_encryption_enabled, false)
  point_in_time_recovery_enabled = try(var.scrape_jobs_table_config.point_in_time_recovery_enabled, false)

  attributes = [
    { name = "id", type = "S" },
    { name = "type", type = "S" },
    { name = "status", type = "S" }
  ]

  global_secondary_indexes = [
    {
      name            = "TypeByStatusGSI"
      hash_key        = "type"
      range_key       = "status"
      read_capacity   = try(var.scrape_jobs_table_config.type_by_status_gsi_config.read_capacity, null)
      write_capacity  = try(var.scrape_jobs_table_config.type_by_status_gsi_config.write_capacity, null)
      projection_type = "KEYS_ONLY"
    }
  ]

  tags = merge(
    {
      DynamoDBTable = "scrape-jobs-${var.environment}"
    },
    var.tags
  )
}

module "scraped_content_table" {
  source = "terraform-aws-modules/dynamodb-table/aws"

  name     = "ScrapedContent"
  hash_key = "url"

  billing_mode   = try(var.scraped_content_table_config.billing_mode, "PAY_PER_REQUEST")
  read_capacity  = try(var.scraped_content_table_config.read_capacity, null)
  write_capacity = try(var.scraped_content_table_config.write_capacity, null)

  server_side_encryption_enabled = try(var.scraped_content_table_config.server_side_encryption_enabled, false)
  point_in_time_recovery_enabled = try(var.scraped_content_table_config.point_in_time_recovery_enabled, false)

  attributes = [
    {
      name = "url"
      type = "S"
    },
    {
      name = "status"
      type = "S"
    },
    {
      name = "type"
      type = "S"
    }
  ]

  global_secondary_indexes = [
    {
      name            = "StatusByTypeGSI"
      hash_key        = "status"
      range_key       = "type"
      projection_type = "KEYS_ONLY"
      read_capacity   = try(var.scraped_content_table_config.status_by_type_gsi_config.read_capacity, null)
      write_capacity  = try(var.scraped_content_table_config.status_by_type_gsi_config.write_capacity, null)
    }
  ]

  tags = merge(
    {
      DynamoDBTable = "scraped-content-${var.environment}"
    },
    var.tags
  )
}

module "user_message_logs" {
  source = "terraform-aws-modules/dynamodb-table/aws"

  name     = "UserMessageLogs"
  hash_key = "id"

  billing_mode   = try(var.user_message_logs_table_config.billing_mode, "PAY_PER_REQUEST")
  read_capacity  = try(var.user_message_logs_table_config.read_capacity, null)
  write_capacity = try(var.user_message_logs_table_config.write_capacity, null)

  server_side_encryption_enabled = try(var.user_message_logs_table_config.server_side_encryption_enabled, false)
  point_in_time_recovery_enabled = try(var.user_message_logs_table_config.point_in_time_recovery_enabled, false)

  attributes = [
    { name = "id", type = "S" },
  ]

  tags = merge(
    {
      DynamoDBTable = "user-message-logs-${var.environment}"
    },
    var.tags
  )
}

module "properties" {
  source = "terraform-aws-modules/dynamodb-table/aws"

  name     = "Properties"
  hash_key = "id"

  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 1

  attributes = [
    { name = "id", type = "N" },
    { name = "city", type = "S" },
    { name = "district", type = "S" },
    { name = "debt_free_price", type = "N" },
    { name = "crawled", type = "N" }
  ]

  global_secondary_indexes = [
    {
      name               = "CityByDebtFreePriceGSI"
      hash_key           = "city"
      range_key          = "debt_free_price"
      read_capacity      = 1
      write_capacity     = 1
      projection_type    = "INCLUDE"
      non_key_attributes = ["district", "building_type", "housing_type", "plot_ownership", "number_of_rooms"]
    },
    {
      name               = "DistrictByDebtFreePriceGSI"
      hash_key           = "district"
      range_key          = "debt_free_price"
      read_capacity      = 1
      write_capacity     = 1
      projection_type    = "INCLUDE"
      non_key_attributes = ["city", "building_type", "housing_type", "plot_ownership", "number_of_rooms"]
    },
    {
      name               = "CrawledUrlGSI"
      hash_key           = "crawled"
      projection_type    = "INCLUDE"
      non_key_attributes = ["url"]
      read_capacity      = 1
      write_capacity     = 1
    }
  ]

  tags = var.enable_tags ? {
    Environment = var.tag_environment
    Terraform   = true
  } : null
}

module "checkpoints" {
  source = "terraform-aws-modules/dynamodb-table/aws"

  name      = "Checkpoints"
  hash_key  = "PK"
  range_key = "SK"

  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 1

  attributes = [
    { name = "PK", type = "S" },
    { name = "SK", type = "S" }
  ]

  tags = var.enable_tags ? {
    Environment = var.tag_environment
    Terraform   = true
  } : null
}

module "scrape_jobs_table" {
  source = "terraform-aws-modules/dynamodb-table/aws"

  name     = "ScrapeJobs"
  hash_key = "id"

  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 1

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
      read_capacity   = 1
      write_capacity  = 1
      projection_type = "KEYS_ONLY"
    }
  ]

  tags = var.enable_tags ? {
    Environment = var.tag_environment
    Terraform   = true
  } : null
}

module "scraped_content_table" {
  source = "terraform-aws-modules/dynamodb-table/aws"

  name     = "ScrapedContent"
  hash_key = "url"

  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 1

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
      read_capacity   = 1
      write_capacity  = 1
    }
  ]

  tags = var.enable_tags ? {
    Environment = var.tag_environment
    Terraform   = true
  } : null
}

module "user_message_logs" {
  source = "terraform-aws-modules/dynamodb-table/aws"

  name     = "UserMessageLogs"
  hash_key = "id"

  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 1

  attributes = [
    { name = "id", type = "S" },
  ]

  tags = var.enable_tags ? {
    Environment = var.tag_environment
    Terraform   = true
  } : null
}

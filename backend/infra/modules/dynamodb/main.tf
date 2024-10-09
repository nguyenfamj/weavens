module "properties" {
  source = "terraform-aws-modules/dynamodb-table/aws"

  name     = "Properties"
  hash_key = "id"

  billing_mode   = "PROVISIONED"
  read_capacity  = 3
  write_capacity = 3

  attributes = [
    { name = "id", type = "N" },
    { name = "city", type = "S" },
    { name = "sales_price", type = "N" },
    { name = "translated", type = "N" },
    { name = "crawled", type = "N" }
  ]

  global_secondary_indexes = [
    {
      name            = "GSI1"
      hash_key        = "city"
      range_key       = "sales_price"
      read_capacity   = 3
      write_capacity  = 3
      projection_type = "ALL"
    },
    {
      name               = "GSI2"
      hash_key           = "crawled"
      projection_type    = "INCLUDE"
      non_key_attributes = ["url"]
      read_capacity      = 3
      write_capacity     = 3
    },
    {
      name               = "GSI3"
      hash_key           = "translated"
      projection_type    = "INCLUDE"
      non_key_attributes = ["completed_renovations", "future_renovations"]
      read_capacity      = 3
      write_capacity     = 3
    }
  ]

  tags = {
    Environment = "production"
    Terraform   = true
  }
}

module "checkpoints" {
  source = "terraform-aws-modules/dynamodb-table/aws"

  name      = "Checkpoints"
  hash_key  = "PK"
  range_key = "SK"

  billing_mode   = "PROVISIONED"
  read_capacity  = 3
  write_capacity = 3

  attributes = [
    { name = "PK", type = "S" },
    { name = "SK", type = "S" }
  ]

  tags = {
    Environment = "production"
    Terraform   = true
  }
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
  ]

  tags = {
    Environment = "production"
    Terraform   = true
  }
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
  ]

  tags = {
    Environment = "production"
    Terraform   = true
  }
}

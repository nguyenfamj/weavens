resource "aws_dynamodb_table" "oikotie_properties" {
  name           = var.property_table_name
  billing_mode   = "PROVISIONED"
  read_capacity  = 3
  write_capacity = 3
  hash_key       = "id"

  attribute {
    name = "id"
    type = "N"
  }

  attribute {
    name = "city"
    type = "S"
  }

  attribute {
    name = "sales_price"
    type = "N"
  }

  attribute {
    name = "translated"
    type = "N"
  }

  attribute {
    name = "crawled"
    type = "N"
  }

  global_secondary_index {
    name            = "GSI1"
    hash_key        = "city"
    range_key       = "sales_price"
    read_capacity   = 3
    write_capacity  = 3
    projection_type = "ALL"
  }

  global_secondary_index {
    name               = "GSI2"
    hash_key           = "crawled"
    projection_type    = "INCLUDE"
    non_key_attributes = ["url"]
    read_capacity      = 3
    write_capacity     = 3
  }

  global_secondary_index {
    name               = "GSI3"
    hash_key           = "translated"
    projection_type    = "INCLUDE"
    non_key_attributes = ["completed_renovations", "future_renovations"]
    read_capacity      = 3
    write_capacity     = 3
  }

  tags = {
    Name = var.property_table_name
  }
}

resource "aws_dynamodb_table" "chat_histories" {
  name           = var.chat_histories_table_name
  billing_mode   = "PROVISIONED"
  read_capacity  = 3
  write_capacity = 3
  hash_key       = "SessionId"

  attribute {
    name = "SessionId"
    type = "S"
  }

  tags = {
    Name = var.chat_histories_table_name
  }
}

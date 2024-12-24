data "aws_ssm_parameter" "production_openai_api_key" {
  name = "/crux/production/openai_api_key"
}

data "aws_ssm_parameter" "production_firecrawl_api_key" {
  name = "/crux/production/firecrawl_api_key"
}

data "aws_ssm_parameter" "production_backend_image_tag" {
  name = "/crux/production/backend_image_tag"
}

data "aws_dynamodb_table" "properties" {
  name = "Properties"
}

data "aws_dynamodb_table" "chat_checkpoints" {
  name = "Checkpoints"
}

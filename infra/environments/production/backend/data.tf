data "aws_ssm_parameter" "production_openai_api_key" {
  name = "/weavens/production/openai_api_key"
}

data "aws_ssm_parameter" "production_firecrawl_api_key" {
  name = "/weavens/production/firecrawl_api_key"
}

data "aws_ssm_parameter" "production_backend_image_tag" {
  name = "/weavens/production/backend_image_tag"
}

data "aws_dynamodb_table" "properties" {
  name = "Properties"
}

data "aws_dynamodb_table" "chat_checkpoints" {
  name = "Checkpoints"
}

data "aws_dynamodb_table" "user_message_logs" {
  name = "UserMessageLogs"
}

data "aws_ssm_parameter" "ecs_optimized_ami" {
  name = "/aws/service/ecs/optimized-ami/amazon-linux-2/recommended"
}

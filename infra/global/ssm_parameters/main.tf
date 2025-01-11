resource "aws_ssm_parameter" "production_openai_api_key" {
  name  = "/weavens/production/openai_api_key"
  type  = "SecureString"
  value = var.PRODUCTION_BACKEND_OPENAI_API_KEY
}

resource "aws_ssm_parameter" "production_firecrawl_api_key" {
  name  = "/weavens/production/firecrawl_api_key"
  type  = "SecureString"
  value = var.PRODUCTION_BACKEND_FIRECRAWL_API_KEY
}

resource "aws_ssm_parameter" "production_backend_image_tag" {
  name  = "/weavens/production/backend_image_tag"
  type  = "SecureString"
  value = var.PRODUCTION_BACKEND_IMAGE_TAG
}


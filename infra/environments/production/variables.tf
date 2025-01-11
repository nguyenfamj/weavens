variable "environment" {
  type        = string
  description = "The environment to deploy to"
}

variable "aws_region" {
  type        = string
  description = "The default AWS region to deploy to"
}

variable "aws_profile" {
  type        = string
  description = "The AWS profile to use"
}

variable "backend_image_version_tag" {
  type        = string
  description = "The version tag for the backend image"
}


variable "production_openai_api_key" {
  type        = string
  description = "The OpenAI API key for the production environment"
}

variable "production_firecrawl_api_key" {
  type        = string
  description = "The FireCrawl API key for the production environment"
}

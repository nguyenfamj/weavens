variable "PRODUCTION_BACKEND_OPENAI_API_KEY" {
  type        = string
  description = "The API key for the OpenAI API for the backend"
}

variable "PRODUCTION_BACKEND_FIRECRAWL_API_KEY" {
  type        = string
  description = "The API key for the FireCrawl API for the backend"
}

variable "PRODUCTION_BACKEND_IMAGE_TAG" {
  type        = string
  description = "The image tag for the backend"
}

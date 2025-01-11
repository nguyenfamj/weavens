variable "environment" {
  type        = string
  description = "The environment to deploy to"
}

variable "tags" {
  type        = map(string)
  description = "The tags to apply to the resources"
}

variable "vpc_private_subnets" {
  type        = list(string)
  description = "The private subnets to deploy the ECS service in"
}

variable "ecr_backend_repository_name" {
  type        = string
  description = "The ECR repository name for the backend"
}

variable "backend_image_version_tag" {
  type        = string
  description = "The version tag for the backend image"
}

variable "opensearch_domain" {
  type        = string
  description = "The OpenSearch domain for search queries made by the backend"
}

variable "production_openai_api_key" {
  type        = string
  description = "The OpenAI API key for the production environment"
}

variable "production_firecrawl_api_key" {
  type        = string
  description = "The FireCrawl API key for the production environment"
}

variable "backend_ecs_alb_target_group_ex_ecs_arn" {
  type        = string
  description = "The ARN of the target group for the backend ECS ALB"
}

variable "backend_ecs_alb_security_group_id" {
  type        = string
  description = "The ID of the security group for the backend ECS ALB"
}

variable "backend_ecs_autoscaling_group_arn" {
  type        = string
  description = "The ARN of the autoscaling group for the backend ECS"
}

variable "backend_dynamodb_tables_access_policy_arn" {
  type        = string
  description = "The ARN of the IAM policy for the backend DynamoDB tables access"
}

variable "backend_opensearch_access_policy_arn" {
  type        = string
  description = "The ARN of the IAM policy for the backend OpenSearch access"
}

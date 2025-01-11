variable "environment" {
  type        = string
  description = "The environment to deploy to"
}

variable "tags" {
  type        = map(string)
  description = "The tags to apply to the resources"
}

variable "ecr_backend_repository_name" {
  type        = string
  description = "The name of the backend ECR repository"
}

variable "backend_image_version_tag" {
  type        = string
  description = "The version tag for the backend image"
}

variable "backend_ecs_alb_target_group_ex_ecs_arn" {
  type        = string
  description = "The ARN of the target group for the backend ECS ALB"
}

variable "backend_ecs_autoscaling_security_group_id" {
  type        = string
  description = "The ID of the security group for the backend ECS autoscaling group"
}

variable "backend_ecs_alb_security_group_id" {
  type        = string
  description = "The ID of the security group for the backend ECS ALB"
}

variable "production_openai_api_key" {
  type        = string
  description = "The OpenAI API key for the production environment"
}

variable "production_firecrawl_api_key" {
  type        = string
  description = "The FireCrawl API key for the production environment"
}

variable "opensearch_domain" {
  type        = string
  description = "The OpenSearch domain for the production environment"
}

variable "vpc_private_subnets" {
  type        = list(string)
  description = "The private subnets to deploy the ECS service in"
}

variable "dynamo_es_property_lambda_sg_id" {
  type        = string
  description = "The ID of the security group for the DynamoDB to OpenSearch Lambda sync"
}

variable "backend_dynamodb_tables_access_policy_arn" {
  type        = string
  description = "The ARN of the IAM policy for the backend DynamoDB tables access"
}

variable "backend_opensearch_access_policy_arn" {
  type        = string
  description = "The ARN of the IAM policy for the backend OpenSearch access"
}

module "autoscaling" {
  source = "./autoscaling"

  environment = var.environment
  tags        = var.tags

  backend_ecs_autoscaling_sg_id = var.backend_ecs_autoscaling_security_group_id

  vpc_private_subnets = var.vpc_private_subnets
}

module "ecs" {
  source = "./ecs"

  environment = var.environment
  tags        = var.tags

  vpc_private_subnets = var.vpc_private_subnets

  # Backend
  ecr_backend_repository_name               = var.ecr_backend_repository_name
  backend_image_version_tag                 = var.backend_image_version_tag
  backend_ecs_alb_target_group_ex_ecs_arn   = var.backend_ecs_alb_target_group_ex_ecs_arn
  backend_ecs_alb_security_group_id         = var.backend_ecs_alb_security_group_id
  backend_ecs_autoscaling_group_arn         = module.autoscaling.backend_ecs_autoscaling_group_arn
  backend_dynamodb_tables_access_policy_arn = var.backend_dynamodb_tables_access_policy_arn
  backend_opensearch_access_policy_arn      = var.backend_opensearch_access_policy_arn

  production_openai_api_key    = var.production_openai_api_key
  production_firecrawl_api_key = var.production_firecrawl_api_key
  opensearch_domain            = var.opensearch_domain
}

module "lambda" {
  source = "./lambda"

  environment = var.environment
  tags        = var.tags

  private_subnet_ids              = var.vpc_private_subnets
  dynamo_es_property_lambda_sg_id = var.dynamo_es_property_lambda_sg_id
}

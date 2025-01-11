
provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

module "common_tags" {
  source      = "../../modules/tags"
  environment = var.environment
}

module "networking" {
  source = "./networking"

  environment = var.environment
  tags        = merge(module.common_tags.tags, { Type = "networking" })
}


module "storage" {
  source = "./storage"

  environment = var.environment
  tags        = merge(module.common_tags.tags, { Type = "storage" })

  vpc_id             = module.networking.app_vpc_id
  vpc_cidr           = module.networking.app_vpc_cidr
  private_subnet_ids = module.networking.app_vpc_private_subnets

  depends_on = [module.common_tags, module.networking]
}

module "compute" {
  source = "./compute"

  environment = var.environment
  tags        = merge(module.common_tags.tags, { Type = "compute" })

  vpc_private_subnets = module.networking.app_vpc_private_subnets

  ecr_backend_repository_name               = module.storage.ecr_backend_repository_name
  backend_image_version_tag                 = var.backend_image_version_tag
  backend_ecs_alb_target_group_ex_ecs_arn   = module.networking.backend_ecs_alb_target_group_ex_ecs_arn
  backend_ecs_autoscaling_security_group_id = module.networking.backend_ecs_autoscaling_security_group_id
  backend_ecs_alb_security_group_id         = module.networking.backend_ecs_alb_security_group_id
  backend_dynamodb_tables_access_policy_arn = module.iam.backend_dynamodb_tables_access_policy_arn
  backend_opensearch_access_policy_arn      = module.iam.backend_opensearch_access_policy_arn

  # Lambda
  dynamo_es_property_lambda_sg_id = module.networking.dynamo_es_property_lambda_sg_id

  # Environment variables
  production_openai_api_key    = var.production_openai_api_key
  production_firecrawl_api_key = var.production_firecrawl_api_key
  opensearch_domain            = module.storage.opensearch_domain_endpoint

  depends_on = [module.common_tags, module.networking, module.storage]
}

module "iam" {
  source = "./common/iam"

  environment = var.environment
  tags        = merge(module.common_tags.tags, { Type = "iam" })

  opensearch_domain_arn = module.storage.opensearch_domain_arn
}

output "github_actions_access_key_id" {
  value = module.iam.github_actions_access_key_id
}

output "github_actions_secret_access_key" {
  value     = module.iam.github_actions_secret_access_key
  sensitive = true
}

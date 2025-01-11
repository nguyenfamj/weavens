variable "environment" {
  type        = string
  description = "The environment to deploy to"
}

variable "tags" {
  type        = map(string)
  description = "The tags to apply to the networking resources"
}


module "vpc" {
  source = "./vpc"

  environment = var.environment
  tags        = var.tags
}

module "alb" {
  source = "./alb"

  environment = var.environment
  tags        = var.tags

  vpc_id             = module.vpc.app_vpc_id
  vpc_public_subnets = module.vpc.app_vpc_public_subnets
  vpc_cidr           = module.vpc.app_vpc_cidr
}

module "security_groups" {
  source = "./security_groups"

  environment = var.environment
  tags        = var.tags

  vpc_id                            = module.vpc.app_vpc_id
  backend_ecs_alb_security_group_id = module.alb.backend_ecs_alb_security_group_id

  depends_on = [module.alb]
}

# Outputs
output "app_vpc_id" {
  value = module.vpc.app_vpc_id
}

output "app_vpc_public_subnets" {
  value = module.vpc.app_vpc_public_subnets
}

output "app_vpc_private_subnets" {
  value = module.vpc.app_vpc_private_subnets
}

output "app_vpc_cidr" {
  value = module.vpc.app_vpc_cidr
}

output "app_vpc_default_security_group_id" {
  value = module.vpc.app_vpc_default_security_group_id
}

output "backend_ecs_alb_target_group_ex_ecs_arn" {
  value = module.alb.backend_ecs_alb_target_group_ex_ecs_arn
}

output "backend_ecs_autoscaling_security_group_id" {
  value = module.security_groups.backend_ecs_autoscaling_security_group_id
}

output "backend_ecs_alb_security_group_id" {
  value = module.alb.backend_ecs_alb_security_group_id
}

output "dynamo_es_property_lambda_sg_id" {
  value = module.security_groups.dynamo_es_property_lambda_sg_id
}

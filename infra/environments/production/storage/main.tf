variable "environment" {
  type        = string
  description = "The environment to deploy to"
}

variable "tags" {
  type        = map(string)
  description = "The tags to apply to the resources"
}

variable "vpc_id" {
  type        = string
  description = "The ID of the VPC"
}

variable "vpc_cidr" {
  type        = string
  description = "The CIDR block of the VPC"
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "The IDs of the private subnets"
}


module "dynamodb" {
  source = "./dynamodb"

  environment = var.environment
  tags        = var.tags
}

module "opensearch" {
  source = "./opensearch"

  environment = var.environment
  tags        = var.tags

  vpc_cidr = var.vpc_cidr
  vpc_id   = var.vpc_id

  private_subnet_ids = var.private_subnet_ids
}


module "ecr" {
  source = "./ecr"

  environment = var.environment
  tags        = var.tags
}


# Outputs
output "ecr_backend_repository_name" {
  value = module.ecr.ecr_backend_repository_name
}

output "opensearch_domain_endpoint" {
  value = module.opensearch.opensearch_domain_endpoint
}

output "opensearch_domain_arn" {
  value = module.opensearch.opensearch_domain_arn
}

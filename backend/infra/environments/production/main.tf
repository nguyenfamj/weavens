terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

provider "aws" {
  region = "eu-north-1"
}

data "terraform_remote_state" "ecr" {
  backend = "s3"
  config = {
    bucket = "terraform-state-crux"
    key    = "globalECR/terraform.tfstate"
    region = "eu-north-1"
  }
}

module "vpc" {
  source = "./vpc"
}

module "dynamodb" {
  source = "../../modules/dynamodb"
}

module "backend" {
  source = "./backend"

  vpc_public_subnets         = module.vpc.app_vpc_public_subnets
  vpc_id                     = module.vpc.app_vpc_id
  vpc_cidr                   = module.vpc.app_vpc_cidr
  backend_ecr_repository_url = data.terraform_remote_state.ecr.outputs.backend_ecr_repository_url
  opensearch_domain_arn      = module.opensearch.search_domain_arn
}

module "frontend" {
  source = "./frontend"
}

module "opensearch" {
  source = "./opensearch"

  stage              = "production"
  vpc_id             = module.vpc.app_vpc_id
  vpc_cidr           = module.vpc.app_vpc_cidr
  private_subnet_ids = module.vpc.app_vpc_private_subnets
}

module "lambda_dynamo_es_property_sync" {
  source = "./lambdas/dynamo-es-property-sync"

  opensearch_domain     = module.opensearch.search_instance_endpoint
  opensearch_domain_arn = module.opensearch.search_domain_arn
  private_subnet_ids    = module.vpc.app_vpc_private_subnets
  vpc_id                = module.vpc.app_vpc_id
}

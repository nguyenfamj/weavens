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
}

module "frontend" {
  source = "./frontend"
}

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
    docker = {
      source = "kreuzwerker/docker"
    }
  }
}

provider "aws" {
  region  = "eu-north-1"
  profile = "nova.developer"

  assume_role {
    role_arn = "arn:aws:iam::484907490685:role/InfrastructureAdmin"
  }
}

provider "docker" {
  registry_auth {
    address  = format("%v.dkr.ecr.%v.amazonaws.com", data.aws_caller_identity.this.account_id, data.aws_region.current.name)
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}

module "dynamodb" {
  source = "../../modules/dynamodb"
}

module "ecr" {
  source = "./ecr"
}

module "docs_scraper" {
  source = "./docs_scraper"
}

module "vpc" {
  source = "./vpc"
}

module "ec2" {
  source = "./ec2"

  vpc_id                    = module.vpc.vpc_id
  public_subnet_ids         = module.vpc.public_subnet_ids
  private_subnet_ids        = module.vpc.private_subnet_ids
  default_security_group_id = module.vpc.default_security_group_id
}

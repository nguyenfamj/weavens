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
  profile = "default"
}

provider "docker" {
  registry_auth {
    address  = format("%v.dkr.ecr.%v.amazonaws.com", data.aws_caller_identity.this.account_id, data.aws_region.current.name)
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}

module "iam" {
  source = "./iam"
}

module "dynamodb" {
  source = "./dynamodb"
}

module "ecr" {
  source = "./ecr"
}

module "lambda" {
  source = "./lambda"

  image_uri = module.ecr.image_uri
}

module "api_gateway" {
  source = "./api_gateway"

  lambda_function_arn = module.lambda.lambda_function_arn
}

module "docs_scraper" {
  source = "./docs_scraper"
}

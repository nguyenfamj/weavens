data "aws_availability_zones" "available" {}

locals {
  name = "production-vpc"

  vpc_cidr = "10.0.0.0/16"
  azs      = slice(data.aws_availability_zones.available.names, 0, 3)

  tags = {
    Terraform   = "true"
    Environment = "production"
  }
}

output "app_vpc_public_subnets" {
  value = module.vpc.public_subnets
}

output "app_vpc_private_subnets" {
  value = module.vpc.private_subnets
}

output "app_vpc_id" {
  value = module.vpc.vpc_id
}

output "app_vpc_cidr" {
  value = local.vpc_cidr
}

# VPC
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = local.name
  cidr = local.vpc_cidr

  azs             = local.azs
  private_subnets = [for k, v in local.azs : cidrsubnet(local.vpc_cidr, 4, k)]
  public_subnets  = [for k, v in local.azs : cidrsubnet(local.vpc_cidr, 8, k + 48)]

  enable_nat_gateway = true
  single_nat_gateway = true

  tags = local.tags
}

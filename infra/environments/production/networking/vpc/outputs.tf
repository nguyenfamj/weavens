output "app_vpc_default_security_group_id" {
  value = module.app_vpc.default_security_group_id
}

output "app_vpc_public_subnets" {
  value = module.app_vpc.public_subnets
}

output "app_vpc_private_subnets" {
  value = module.app_vpc.private_subnets
}

output "app_vpc_id" {
  value = module.app_vpc.vpc_id
}

output "app_vpc_cidr" {
  value = local.vpc_cidr
}

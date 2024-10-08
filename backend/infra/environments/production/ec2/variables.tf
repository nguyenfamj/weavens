variable "vpc_id" {
  description = "The ID of the VPC"
}

variable "public_subnet_ids" {
  description = "The IDs of the public subnets"
}

variable "private_subnet_ids" {
  description = "The IDs of the private subnets"
}

variable "default_security_group_id" {
  description = "The ID of the default security group"
}

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
  description = "The VPC ID"
}

variable "vpc_public_subnets" {
  type        = list(string)
  description = "The public subnets to deploy the ALB in"
}

variable "vpc_cidr" {
  type        = string
  description = "The CIDR block of the VPC"
}

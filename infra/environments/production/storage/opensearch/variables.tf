variable "tags" {
  type        = map(string)
  description = "The tags to apply to the OpenSearch domain"
}

variable "environment" {
  type        = string
  description = "The environment to deploy to"
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

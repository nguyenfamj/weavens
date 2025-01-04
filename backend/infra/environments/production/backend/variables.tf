variable "vpc_public_subnets" {
  type        = list(string)
  description = "The public subnets for the VPC"
}

variable "vpc_id" {
  type        = string
  description = "The ID of the VPC"
}

variable "vpc_cidr" {
  type        = string
  description = "The CIDR of the VPC"
}

variable "backend_ecr_repository_url" {
  type        = string
  description = "The URL of the ECR repository for the backend"
}

variable "opensearch_domain_arn" {
  type        = string
  description = "The ARN of the OpenSearch domain"
}

variable "environment" {
  type        = string
  description = "The environment to deploy the security group in"
}

variable "tags" {
  type        = map(string)
  description = "The tags to apply to the security group"
}

variable "vpc_id" {
  type        = string
  description = "The ID of the VPC to deploy the security group in"
}

variable "backend_ecs_alb_security_group_id" {
  type        = string
  description = "The ID of the security group for the backend ECS ALB"
}

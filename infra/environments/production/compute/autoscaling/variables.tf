variable "environment" {
  type        = string
  description = "The environment to deploy the autoscaling group in"
}

variable "tags" {
  type        = map(string)
  description = "The tags to apply to the autoscaling group"
}

variable "vpc_private_subnets" {
  type        = list(string)
  description = "The private subnets to deploy the autoscaling group in"
}

variable "backend_ecs_autoscaling_sg_id" {
  type        = string
  description = "The ID of the security group for the backend ECS autoscaling group"
}

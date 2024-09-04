variable "ecr_repo_name" {
  description = "The name of the ECR repository"
  type        = string
  default     = "house_hunt_repo"
}

variable "region" {
  description = "The region in which the ECR repository is created"
  type        = string
  default     = "us-east-1"
}

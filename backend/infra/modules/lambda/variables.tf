variable "lambda_role_arn" {
  description = "The ARN of the IAM role for the Lambda function"
  type        = string
}

variable "ecr_repo_url" {
  description = "The URL of the ECR repository"
  type        = string
}

variable "lambda_function_name" {
  description = "The name of the Lambda function"
  type        = string
}

variable "image_id" {
  description = "The ID of the deployed Docker image to ECR"
  type        = string
}

variable "iam_role_policy_attachment_id" {
  description = "The ID of the IAM role policy attachment"
  type        = string
}

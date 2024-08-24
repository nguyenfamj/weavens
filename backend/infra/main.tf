terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

# module "dynamoDB" {
#   source                    = "./modules/dynamodb"
#   property_table_name       = local.property_table_name
#   chat_histories_table_name = local.chat_histories_table_name
# }

# --- ECR ---
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

resource "aws_ecr_repository" "house_hunt_ecr" {
  name                 = var.ecr_repo_name
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }
}

locals {
  repo_url = aws_ecr_repository.house_hunt_ecr.repository_url
}

resource "null_resource" "image" {
  provisioner "local-exec" {
    command = <<EOF
      aws ecr get-login-password --region ${var.region} | docker login --username AWS --password-stdin ${local.repo_url}
      docker build --platform linux/arm64 -t ${local.repo_url}:latest ./..
      docker push ${local.repo_url}:latest
    EOF
  }
}

data "aws_ecr_image" "image" {
  repository_name = aws_ecr_repository.house_hunt_ecr.name
  image_tag       = "latest"
  depends_on      = [null_resource.image]
}

# --- IAM ---
resource "aws_iam_role" "lambda" {
  name = "lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# --- Lambda ---
resource "aws_lambda_function" "api" {
  function_name = "api"
  role          = aws_iam_role.lambda.arn
  image_uri     = "${aws_ecr_repository.house_hunt_ecr.repository_url}:latest"
  architectures = ["arm64"]
  package_type  = "Image"
  timeout       = 20

  depends_on = [
    null_resource.image,
    aws_iam_role_policy_attachment.lambda
  ]
}

resource "aws_lambda_function_url" "api" {
  function_name      = aws_lambda_function.api.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = true
    allow_origins     = ["*"]
    allow_methods     = ["*"]
    allow_headers     = ["*"]
  }
}

output "api_url" {
  value = aws_lambda_function_url.api.function_url
}


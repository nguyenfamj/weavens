variable "environment" {
  type        = string
  description = "The environment to deploy to"
}

variable "tags" {
  type        = map(string)
  description = "The tags to apply to the ecr repositories"
}

locals {
  name = "${var.environment}-backend-ecr"
}


resource "aws_ecr_repository" "weavens_backend" {
  name                 = local.name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
  }

  tags     = var.tags
  tags_all = var.tags
}

resource "aws_ecr_lifecycle_policy" "weavens_backend" {
  repository = aws_ecr_repository.weavens_backend.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 3 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 3
      }
      action = {
        type = "expire"
      }
    }]
  })
}


# Outputs
output "ecr_backend_repository_name" {
  value = aws_ecr_repository.weavens_backend.name
}

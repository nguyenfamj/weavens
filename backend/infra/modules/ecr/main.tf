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




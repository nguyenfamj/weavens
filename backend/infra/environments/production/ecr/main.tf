module "docker_image" {
  source = "terraform-aws-modules/lambda/aws//modules/docker-build"

  create_ecr_repo = true
  ecr_repo        = "house-hunt"

  use_image_tag = true
  image_tag     = "latest"

  source_path = "../../../../backend"

  ecr_repo_tags = {
    Environment = "production"
    Terraform   = true
  }
}

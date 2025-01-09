data "aws_s3_bucket" "terraform_state" {
  bucket = "terraform-state-crux"
}

data "aws_dynamodb_table" "terraform_state_locks" {
  name = "TerraformStateLocks"
}

data "aws_ecr_repository" "backend" {
  name = "crux-backend"
}

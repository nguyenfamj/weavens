terraform {
  backend "s3" {
    bucket = "terraform-state-crux"
    key    = "terraform.tfstate"
    region = "eu-north-1"
    assume_role = {
      role_arn = "arn:aws:iam::484907490685:role/InfrastructureAdmin"
    }
    dynamodb_table = "TerraformStateLocks"
  }
}

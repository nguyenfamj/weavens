terraform {
  backend "s3" {
    bucket         = "terraform-state-crux"
    key            = "globalIAM/terraform.tfstate"
    region         = "eu-north-1"
    dynamodb_table = "TerraformStateLocks"
    encrypt        = true
  }
}

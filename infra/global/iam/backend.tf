terraform {
  backend "s3" {
    bucket         = "terraform-state-weavens"
    key            = "globalIAM/terraform.tfstate"
    region         = "eu-north-1"
    dynamodb_table = "TerraformStateLocks"
    encrypt        = true
  }
}

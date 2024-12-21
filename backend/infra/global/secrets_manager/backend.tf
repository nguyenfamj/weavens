terraform {
  backend "s3" {
    bucket         = "terraform-state-crux"
    key            = "globalSecretsManager/terraform.tfstate"
    region         = "eu-north-1"
    dynamodb_table = "TerraformStateLocks"
    encrypt        = true
  }
}

terraform {
  backend "s3" {
    bucket         = "terraform-state-crux"
    key            = "global_admin/terraform.tfstate"
    region         = "eu-north-1"
    dynamodb_table = "TerraformStateLocks"
    profile        = "global_admin"
  }
}

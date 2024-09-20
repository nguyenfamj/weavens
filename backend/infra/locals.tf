locals {
  region = "eu-north-1"

  property_table_name   = "OikotieProperties"
  checkpoint_table_name = "Checkpoints"

  ecr_repo_name        = "house_hunt_repo"
  lambda_function_name = "house_hunt_lambda"
  lambda_timeout       = 10

  api_gateway_name = "house_hunt_api"
}

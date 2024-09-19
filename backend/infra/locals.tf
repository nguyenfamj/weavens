locals {
  region = "eu-north-1"

  property_table_name       = "OikotieProperties"
  chat_histories_table_name = "ChatHistories"

  ecr_repo_name        = "house_hunt_repo"
  lambda_function_name = "house_hunt_lambda"
  lambda_timeout       = 10
}

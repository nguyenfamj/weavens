terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

# module "dynamoDB" {
#   source                    = "./modules/dynamodb"
#   property_table_name       = local.property_table_name
#   chat_histories_table_name = local.chat_histories_table_name
# }

# --- ECR ---
module "ecr" {
  source        = "./modules/ecr"
  ecr_repo_name = local.ecr_repo_name
  region        = local.region
}

# --- IAM ---
module "iam" {
  source = "./modules/iam"

  iam_role_name = "lambda_role"
}

# --- Lambda ---
module "lambda" {
  source = "./modules/lambda"

  lambda_role_arn      = module.iam.lambda_role_arn
  ecr_repo_url         = module.ecr.ecr_repo_url
  lambda_function_name = local.lambda_function_name

  image_id                      = module.ecr.image.id
  iam_role_policy_attachment_id = module.iam.iam_role_policy_attachment.id
}

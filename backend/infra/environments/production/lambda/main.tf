data "aws_caller_identity" "current" {}

module "lambda_function" {
  source = "terraform-aws-modules/lambda/aws"

  function_name  = "house-hunt"
  create_package = false
  timeout        = 20

  create_role     = true
  role_name       = "LambdaExecutionRole"
  attach_policies = true
  policies = [
    "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
    "arn:aws:iam::aws:policy/SecretsManagerReadWrite",
  ]
  number_of_policies = 2

  image_uri     = var.image_uri
  package_type  = "Image"
  architectures = ["arm64"]

  publish = true

  allowed_triggers = {
    APIGatewayAny = {
      service    = "apigateway"
      source_arn = "arn:aws:execute-api:eu-north-1:${data.aws_caller_identity.current.account_id}:*"
    }
  }

  tags = {
    Environment = "production"
    Terraform   = true
  }
}

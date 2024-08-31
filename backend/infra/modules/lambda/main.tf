resource "aws_lambda_function" "api" {
  function_name = var.lambda_function_name
  role          = var.lambda_role_arn
  image_uri     = "${var.ecr_repo_url}:latest"
  architectures = ["arm64"]
  package_type  = "Image"
  timeout       = var.lambda_timeout

  depends_on = [
    var.image_id,
    var.iam_role_policy_attachment_id
  ]
}

resource "aws_lambda_function_url" "api" {
  function_name      = aws_lambda_function.api.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = true
    allow_origins     = ["*"]
    allow_methods     = ["*"]
    allow_headers     = ["*"]
  }
}

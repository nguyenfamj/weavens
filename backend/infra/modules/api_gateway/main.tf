resource "aws_api_gateway_rest_api" "api_gateway" {
  name        = var.api_gateway_name
  description = "API Gateway for the ${var.api_gateway_name} API"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_resource" "health_check" {
  parent_id   = aws_api_gateway_rest_api.api_gateway.root_resource_id
  path_part   = "healthcheck"
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
}


resource "aws_api_gateway_method" "get_health_check" {
  authorization = "NONE"
  http_method   = "GET"
  resource_id   = aws_api_gateway_resource.health_check.id
  rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
}

resource "aws_api_gateway_integration" "lambda_intergration" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  resource_id = aws_api_gateway_resource.health_check.id
  http_method = aws_api_gateway_method.get_health_check.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn

  depends_on = [var.lambda_invoke_arn]
}

resource "aws_api_gateway_deployment" "deployment" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id

  depends_on = [aws_api_gateway_integration.lambda_intergration]
}

resource "aws_api_gateway_stage" "prod" {
  deployment_id = aws_api_gateway_deployment.deployment.id
  rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
  stage_name    = "prod"
}

resource "aws_lambda_permission" "api_gw_lambda" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "apigateway.amazonaws.com"
}

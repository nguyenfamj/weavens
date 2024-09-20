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

resource "aws_api_gateway_integration" "get_health_check" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  resource_id = aws_api_gateway_resource.health_check.id
  http_method = aws_api_gateway_method.get_health_check.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn

  depends_on = [var.lambda_invoke_arn]
}

resource "aws_api_gateway_resource" "api" {
  parent_id   = aws_api_gateway_rest_api.api_gateway.root_resource_id
  path_part   = "api"
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
}

resource "aws_api_gateway_resource" "v1" {
  parent_id   = aws_api_gateway_resource.api.id
  path_part   = "v1"
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
}

resource "aws_api_gateway_resource" "graph" {
  parent_id   = aws_api_gateway_resource.v1.id
  path_part   = "graph"
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
}

resource "aws_api_gateway_resource" "graph_invoke" {
  parent_id   = aws_api_gateway_resource.graph.id
  path_part   = "invoke"
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
}
resource "aws_api_gateway_method" "post_invoke" {
  authorization = "NONE"
  http_method   = "POST"
  resource_id   = aws_api_gateway_resource.graph_invoke.id
  rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
}


resource "aws_api_gateway_integration" "post_graph_invoke" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  resource_id = aws_api_gateway_resource.graph_invoke.id
  http_method = aws_api_gateway_method.post_invoke.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn

  depends_on = [var.lambda_invoke_arn]
}

resource "aws_api_gateway_resource" "graph_stream" {
  parent_id   = aws_api_gateway_resource.graph.id
  path_part   = "stream"
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
}

resource "aws_api_gateway_method" "post_stream" {
  authorization = "NONE"
  http_method   = "POST"
  resource_id   = aws_api_gateway_resource.graph_stream.id
  rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
}

resource "aws_api_gateway_integration" "post_graph_stream" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  resource_id = aws_api_gateway_resource.graph_stream.id
  http_method = aws_api_gateway_method.post_stream.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn

  depends_on = [var.lambda_invoke_arn]
}

resource "aws_api_gateway_deployment" "deployment" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id

  triggers = {
    redeployment = sha1((jsonencode([
      aws_api_gateway_integration.get_health_check.uri,
      aws_api_gateway_integration.post_graph_invoke.uri,
      aws_api_gateway_integration.post_graph_stream.uri
    ])))
  }

  lifecycle {
    create_before_destroy = true
  }
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

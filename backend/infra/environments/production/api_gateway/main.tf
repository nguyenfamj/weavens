module "api_gateway" {
  source = "terraform-aws-modules/apigateway-v2/aws"

  name          = "house-hunt-api"
  protocol_type = "HTTP"

  stage_access_log_settings = {
    create_log_group            = true
    log_group_retention_in_days = 3
    format = jsonencode({
      context = {
        domainName              = "$context.domainName"
        integrationErrorMessage = "$context.integrationErrorMessage"
        protocol                = "$context.protocol"
        requestId               = "$context.requestId"
        requestTime             = "$context.requestTime"
        responseLength          = "$context.responseLength"
        routeKey                = "$context.routeKey"
        stage                   = "$context.stage"
        status                  = "$context.status"
        error = {
          message      = "$context.error.message"
          responseType = "$context.error.responseType"
        }
        identity = {
          sourceIP = "$context.identity.sourceIp"
        }
        integration = {
          error             = "$context.integration.error"
          integrationStatus = "$context.integration.integrationStatus"
        }
      }
    })
  }

  create_domain_name    = false
  create_domain_records = false

  routes = {
    "GET /healthcheck" = {
      integration = {
        uri = var.lambda_function_arn
      }
    }

    "POST /api/v1/graph/invoke" = {
      integration = {
        uri = var.lambda_function_arn
      }
    }

    "POST /api/v1/graph/stream" = {
      integration = {
        uri = var.lambda_function_arn

      }
    }
  }

  tags = {
    Environment = "production"
    Terraform   = true
  }
}

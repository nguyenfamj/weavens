data "aws_dynamodb_table" "properties" {
  name = "${var.environment}-Properties"
}

data "aws_opensearch_domain" "this" {
  domain_name = "weavens-${var.environment}-search"
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "The private subnet IDs"
}

variable "dynamo_es_property_lambda_sg_id" {
  type        = string
  description = "The ID of the security group for the DynamoDB to OpenSearch Lambda sync"
}

module "this" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.17.0"

  function_name = "dynamo-es-property-sync"
  description   = "Lambda function to sync properties from DynamoDB to OpenSearch"

  handler     = "dist/index.handler"
  runtime     = "nodejs20.x"
  timeout     = 30
  memory_size = 128

  source_path = "${path.module}/../../../../../lambdas/dynamo-es-property-sync"

  environment_variables = {
    OPENSEARCH_DOMAIN = "https://${data.aws_opensearch_domain.this.endpoint}"
  }

  vpc_subnet_ids         = var.private_subnet_ids
  vpc_security_group_ids = [var.dynamo_es_property_lambda_sg_id]
  attach_network_policy  = true

  event_source_mapping = {
    dynamodb = {
      event_source_arn  = data.aws_dynamodb_table.properties.stream_arn
      starting_position = "LATEST"
      batch_size        = 100
    }
  }

  attach_policy_statements = true
  policy_statements = {
    dynamodb = {
      effect = "Allow"
      actions = [
        "dynamodb:GetRecords",
        "dynamodb:GetShardIterator",
        "dynamodb:DescribeStream",
        "dynamodb:ListStreams"
      ]
      resources = ["${data.aws_dynamodb_table.properties.arn}/stream/*"]
    }
    opensearch = {
      effect = "Allow"
      actions = [
        "es:ESHttp*"
      ]
      resources = ["${data.aws_opensearch_domain.this.arn}/*"]
    }
  }

  tags = var.tags
}

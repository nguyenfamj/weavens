locals {
  tags = {
    Name        = "dynamo-es-property-sync"
    Environment = "production"
    Terraform   = "true"
  }
}

variable "opensearch_domain" {
  type        = string
  description = "The domain of the OpenSearch domain"
}

variable "opensearch_domain_arn" {
  type        = string
  description = "The ARN of the OpenSearch domain"
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "The private subnet IDs"
}

variable "vpc_id" {
  type        = string
  description = "The VPC ID"
}

data "aws_dynamodb_table" "properties" {
  name = "Properties"
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
    OPENSEARCH_DOMAIN = var.opensearch_domain
  }

  vpc_subnet_ids         = var.private_subnet_ids
  vpc_security_group_ids = [aws_security_group.this.id]
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
      resources = ["${var.opensearch_domain_arn}/*"]
    }
  }

  tags = local.tags
}

# Supporting resources
resource "aws_security_group" "this" {
  name        = "dynamo-es-property-sync-sg"
  description = "Security group for DynamoDB to OpenSearch Lambda sync"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.tags
}

data "aws_dynamodb_table" "properties" {
  name = "${var.environment}-Properties"
}

data "aws_dynamodb_table" "chat_checkpoints" {
  name = "${var.environment}-Checkpoints"
}

data "aws_dynamodb_table" "user_message_logs" {
  name = "${var.environment}-UserMessageLogs"
}

resource "aws_iam_policy" "backend_dynamodb_tables_access" {
  name = "backend-${var.environment}-dynamodb-tables-access"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:PutItem",
          "dynamodb:BatchGetItem"
        ]
        Resource = [
          data.aws_dynamodb_table.properties.arn,
          data.aws_dynamodb_table.chat_checkpoints.arn,
          data.aws_dynamodb_table.user_message_logs.arn,
          "${data.aws_dynamodb_table.properties.arn}/index/*",
        ]
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_policy" "backend_opensearch_access" {
  name = "backend-${var.environment}-opensearch-access"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "es:ESHttp*"
        ]
        Resource = [
          "${var.opensearch_domain_arn}/*"
        ]
      }
    ]
  })

  tags = var.tags
}


# Outputs
output "backend_dynamodb_tables_access_policy_arn" {
  value = aws_iam_policy.backend_dynamodb_tables_access.arn
}

output "backend_opensearch_access_policy_arn" {
  value = aws_iam_policy.backend_opensearch_access.arn
}

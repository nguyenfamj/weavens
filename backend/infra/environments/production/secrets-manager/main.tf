# Secrets Manager
resource "aws_secretsmanager_secret" "app_secrets" {
  name = "crux/production/apps"
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    OPENAI_API_KEY    = var.BACKEND_OPENAI_API_KEY
    FIRECRAWL_API_KEY = var.BACKEND_FIRECRAWL_API_KEY
  })
}

output "app_secrets_arn" {
  value = aws_secretsmanager_secret.app_secrets.arn
}

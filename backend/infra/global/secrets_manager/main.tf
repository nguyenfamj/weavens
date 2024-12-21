# Secrets Manager
resource "aws_secretsmanager_secret" "production_apps_secrets" {
  name = "crux/production/apps_secrets"
}

resource "aws_secretsmanager_secret_version" "production_apps_secrets" {
  secret_id = aws_secretsmanager_secret.production_apps_secrets.id
  secret_string = jsonencode({
    OPENAI_API_KEY    = var.PRODUCTION_BACKEND_OPENAI_API_KEY
    FIRECRAWL_API_KEY = var.PRODUCTION_BACKEND_FIRECRAWL_API_KEY
  })
}

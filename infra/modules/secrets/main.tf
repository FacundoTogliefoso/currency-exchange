# Database credentials
resource "aws_secretsmanager_secret" "db_credentials" {
  name        = "${var.name}-db-credentials"
  description = "Database credentials for Aurora cluster"

  tags = var.tags
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = var.db_username
    password = var.db_password
  })
}

# Banxico API token
resource "aws_secretsmanager_secret" "banxico_token" {
  name        = "${var.name}-banxico-token"
  description = "Banxico API token for exchange rate data"

  tags = var.tags
}

resource "aws_secretsmanager_secret_version" "banxico_token" {
  secret_id = aws_secretsmanager_secret.banxico_token.id
  secret_string = jsonencode({
    token = var.banxico_token
  })
}

# Redis auth token (optional)
resource "aws_secretsmanager_secret" "redis_auth" {
  count       = var.redis_auth_token != "" ? 1 : 0
  name        = "${var.name}-redis-auth"
  description = "Redis authentication token"

  tags = var.tags
}

resource "aws_secretsmanager_secret_version" "redis_auth" {
  count     = var.redis_auth_token != "" ? 1 : 0
  secret_id = aws_secretsmanager_secret.redis_auth[0].id
  secret_string = jsonencode({
    auth_token = var.redis_auth_token
  })
}

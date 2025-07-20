output "db_credentials_arn" {
  value = aws_secretsmanager_secret.db_credentials.arn
}

output "banxico_token_arn" {
  value = aws_secretsmanager_secret.banxico_token.arn
}

output "redis_auth_arn" {
  value = var.redis_auth_token != "" ? aws_secretsmanager_secret.redis_auth[0].arn : null
}

output "db_credentials_name" {
  value = aws_secretsmanager_secret.db_credentials.name
}

output "banxico_token_name" {
  value = aws_secretsmanager_secret.banxico_token.name
}

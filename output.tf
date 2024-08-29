output "secret_arn" {
  value = aws_secretsmanager_secret.db_pass.arn
}

output "db_endpoint_primary" {
  value = local.endpoint
}

output "secret_arn" {
  value = aws_secretsmanager_secret.db_pass.arn
}

output "db_endpoint_primary" {
  value = local.endpoint
}

output "Create_Table_trex" {
  value = module.Create_Table_trex.lambda_function_url
}

output "Create_Table_ticket" {
  value = module.Create_Table.lambda_function_url
}
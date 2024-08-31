resource "random_password" "master" {
  length  = 20
  special = false
  
}

locals {
  #endpoint = module.rds_proxy.proxy_endpoint
  endpoint   = module.aurora_postgresql_v2_primary.cluster_endpoint
  identifier = module.aurora_postgresql_v2_primary.cluster_instances["one"].id
}


resource "aws_secretsmanager_secret" "db_pass" {
  name                    = "${var.platform_name}/database/secret"
  recovery_window_in_days = 0
}




resource "aws_secretsmanager_secret_version" "example" {
  secret_id     = aws_secretsmanager_secret.db_pass.id #pim360
  secret_string = <<EOF
    { 
    "dbname": "pim360", 
    "engine": "postgres", 
    "port": 5432, 
    "host": "${local.endpoint}", 
    "username": "${var.database_username_master}",
    "password": "${random_password.master.result}"
    }
  EOF
}







# resource "aws_secretsmanager_secret" "ticket" {
#   name                    = "ticket-${var.platform_name}-${random_pet.this.id}"
#   recovery_window_in_days = 0
# }

# resource "aws_secretsmanager_secret" "ticket_sec" {
#   name                    = "ticket-${var.platform_name}-${random_pet.this.id}"
#   recovery_window_in_days = 0
#   provider = aws.region2
# }

# resource "aws_secretsmanager_secret_version" "ticket" {
#   secret_id     = aws_secretsmanager_secret.ticket.id #pim360
#   secret_string = <<EOF
#     { 
#     "username": "${var.database_username_tickets}",
#     "password": "${random_password.tickets.result}"
#     }
#   EOF
# }

# resource "aws_secretsmanager_secret_version" "ticket_sec" {
#   secret_id     = aws_secretsmanager_secret.ticket_sec.id #pim360
#   provider = aws.region2
#   secret_string = <<EOF
#     { 
#     "username": "${var.database_username_tickets}",
#     "password": "${random_password.tickets.result}"
#     }
#   EOF
# }

# resource "aws_secretsmanager_secret" "trex" {
#   name                    = "trex-${var.platform_name}-${random_pet.this.id}"
#   recovery_window_in_days = 0
# }

# resource "aws_secretsmanager_secret" "trex_sec" {
#   name                    = "trex-${var.platform_name}-${random_pet.this.id}"
#   recovery_window_in_days = 0

#   provider = aws.region2
# }

# resource "aws_secretsmanager_secret_version" "trex" {
#   secret_id     = aws_secretsmanager_secret.trex.id #pim360
#   secret_string = <<EOF
#     { 
#     "username": "${var.database_username_trex}",
#     "password": "${random_password.trex.result}"
#     }
#   EOF
# }

# resource "aws_secretsmanager_secret_version" "trex_sec" {
#   secret_id     = aws_secretsmanager_secret.trex_sec.id #pim360
#   provider = aws.region2
#   secret_string = <<EOF
#     { 
#     "username": "${var.database_username_trex}",
#     "password": "${random_password.trex.result}"
#     }
#   EOF
# }
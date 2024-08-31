resource "aws_lambda_layer_version" "lambda_layer" {
  filename   = "lambda-func/python-layer.zip"
  layer_name = "t360-layer"

  compatible_runtimes = ["python3.11", "python3.9", "python3.10", "python3.8"]
}


module "Create_Table" {
  source = "./modules/Create_Table"
  layers = [aws_lambda_layer_version.lambda_layer.arn, "arn:aws:lambda:${var.region1}:580247275435:layer:LambdaInsightsExtension:21"]


  function_name              = "Create_Api_Table"
  handler                    = "api.revenue_codes"
  runtime                    = "python3.8"
  architectures              = ["x86_64"]
  create_lambda_function_url = true
  timeout                    = 900
  tracing_mode               = "Active"
  publish                    = true
  store_on_s3                = false
  memory_size                = 1024


  source_path = "${path.module}/lambda-func/src/"

  vpc_subnet_ids         = var.private_subnet_ids
  vpc_security_group_ids = [module.LambdaSecurityGroup.security_group_id]

  environment_variables = {
    SECRET_NAME = "${var.platform_name}/database/secret"
    REGION      = var.region1
  }

  attach_policies    = true
  policies           = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole", "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"]
  number_of_policies = 2

  attach_policy_statements = true
  policy_statements = {
    secrets_manager = {
      effect = "Allow"
      actions = [
        "secretsmanager:GetSecretValue"
      ]
      resources = ["*"]
    }
  }
}


module "Create_Table_trex" {
  source = "./modules/Create_Table"
  layers = [aws_lambda_layer_version.lambda_layer.arn, "arn:aws:lambda:${var.region1}:580247275435:layer:LambdaInsightsExtension:21"]


  function_name              = "Create_Api_Table_trex"
  handler                    = "main.revenue_codes"
  runtime                    = "python3.8"
  architectures              = ["x86_64"]
  create_lambda_function_url = true
  timeout                    = 900
  tracing_mode               = "Active"
  publish                    = true
  store_on_s3                = false
  memory_size                = 1024


  source_path = "${path.module}/lambda-func/trex/"

  vpc_subnet_ids         = var.private_subnet_ids
  vpc_security_group_ids = [module.LambdaSecurityGroup.security_group_id]

  environment_variables = {
    SECRET_NAME = "${var.platform_name}/database/secret"
    REGION      = var.region1
  }

  attach_policies    = true
  policies           = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole", "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"]
  number_of_policies = 2

  attach_policy_statements = true
  policy_statements = {
    secrets_manager = {
      effect = "Allow"
      actions = [
        "secretsmanager:GetSecretValue"
      ]
      resources = ["*"]
    }
    kms = {
      effect = "Allow"
      actions = [
        "kms:Decrypt"
      ]
      resources = ["*"]
    }
  }
}
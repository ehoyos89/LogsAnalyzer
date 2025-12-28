terraform {
    required_version = ">= 1.0.0"

    required_providers {
      aws = {
        source = "hashicorp/aws"
        version = "~> 6.0"
      }
    }
}

# 1. Bucket para los Logs
resource "aws_s3_bucket" "log_bucket" {
  bucket = var.bucket_name
}

# 2. Tópico de SNS para alertas
resource "aws_sns_topic" "alerts" {
  name = "security-alerts-topic"
}

# 3. Función Lambda
resource "aws_lambda_function" "log_analyzer" {
  filename      = "lambda_function_payload.zip"
  function_name = "LogSecurityAnalyzer"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "analyzer.lambda_handler"
  runtime       = "python3.12"
  timeout       = 30

  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.alerts.arn
    }
  }
}

# 4. Permiso para que S3 invoque a la Lambda
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.log_analyzer.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.log_bucket.arn
}

# 5. Configuración del Trigger de S3
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.log_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.log_analyzer.arn
    events              = ["s3:ObjectCreated:*"]
  }
  depends_on = [aws_lambda_permission.allow_s3]
}

# 6. Suscripción para recibir los correos
resource "aws_sns_topic_subscription" "user_updates_sqs_target" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.sns_email 
}
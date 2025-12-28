output "s3_bucket_id" {
  value       = aws_s3_bucket.log_bucket.id
  description = "ID del bucket para subir tus archivos de logs"
}

output "lambda_function_arn" {
  value       = aws_lambda_function.log_analyzer.arn
  description = "ARN de la función Lambda creada"
}

output "sns_topic_arn" {
  value       = aws_sns_topic.alerts.arn
  description = "ARN del tópico SNS para las alertas"
}
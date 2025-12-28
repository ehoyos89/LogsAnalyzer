variable "bucket_name" {
  type        = string
  default     = "tu-nombre-de-bucket"
  description = "Bucket name"
}
  
variable "sns_email" {
  description = "Correo electrónico para recibir las alertas de seguridad"
  type        = string
  # Aquí es donde te llegarán los análisis de la IA
  default     = "tu-correo" 
}

variable "aws_region" {
  description = "Región de AWS donde se desplegarán los recursos"
  type        = string
  default     = "us-east-1"
}
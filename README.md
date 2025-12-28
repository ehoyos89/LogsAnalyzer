# AI-Powered Security Log Analyzer

Sistema automatizado de análisis de logs de seguridad que utiliza AWS Lambda, Amazon Bedrock (Claude 3 Haiku) y notificaciones SNS para detectar y analizar actividad sospechosa en tiempo real.

## 🎯 Características

- **Análisis automático**: Procesa logs de CloudFront/Amplify automáticamente al subirlos a S3
- **Detección inteligente**: Identifica errores HTTP, rutas sensibles y bots maliciosos
- **IA integrada**: Utiliza Claude 3 Haiku para análisis contextual de amenazas
- **Alertas instantáneas**: Notificaciones por email con recomendaciones de seguridad
- **Infraestructura como código**: Desplegado completamente con Terraform

## 🏗️ Arquitectura

```
S3 Bucket → Lambda Function → Amazon Bedrock → SNS Topic → Email Alert
    ↑              ↓              ↓              ↓
 Log Files    Log Analysis   AI Analysis   Security Report
```

### Componentes

- **S3 Bucket**: Almacena los archivos de logs
- **Lambda Function**: Procesa y analiza los logs automáticamente
- **Amazon Bedrock**: Proporciona análisis de IA con Claude 3 Haiku
- **SNS Topic**: Envía alertas por email
- **IAM Roles**: Permisos seguros para todos los servicios

## 🚀 Instalación

### Prerrequisitos

- AWS CLI configurado
- Terraform >= 1.0.0
- Permisos para crear recursos en AWS (S3, Lambda, SNS, Bedrock, IAM)

### Despliegue

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/ehoyos89/LogsAnalyzer.git
   cd LogsAnalyzer
   ```

2. **Configurar variables**
   
   Edita `variables.tf` o crea un archivo `terraform.tfvars`:
   ```hcl
   bucket_name = "tu-bucket-logs-unico"
   sns_email   = "tu-email@ejemplo.com"
   aws_region  = "us-east-1"
   ```

3. **Desplegar infraestructura**
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

4. **Confirmar suscripción**
   
   Revisa tu email y confirma la suscripción al tópico SNS.

## 📊 Uso

### Subir logs para análisis

```bash
aws s3 cp tu-archivo-logs.csv s3://tu-bucket-logs-unico/
```

### Formato de logs soportado

El sistema procesa archivos CSV con las siguientes columnas:
- `c-ip`: Dirección IP del cliente
- `cs-method`: Método HTTP (GET, POST, etc.)
- `cs-uri-stem`: Ruta solicitada
- `sc-status`: Código de estado HTTP
- `cs(User-Agent)`: User Agent del cliente

### Detección automática

El sistema detecta automáticamente:
- **Errores HTTP**: Códigos 4xx y 5xx
- **Rutas sensibles**: `.env`, `.git`, `phpinfo`, `admin`
- **Bots maliciosos**: Assetnote, Censys, y otros scanners

## 🔧 Configuración

### Personalizar detección

Modifica `lambda/analyzer.py` para ajustar los criterios de detección:

```python
# Agregar nuevos patrones sospechosos
is_sensitive_path = any(x in uri.lower() for x in [
    '.env', '.git', 'phpinfo', 'admin', 'wp-admin', 'config'
])

# Detectar nuevos bots
is_bot = any(bot in user_agent for bot in [
    "Assetnote", "Censys", "Shodan", "Nmap"
])
```

## 📈 Outputs

Después del despliegue, obtienes:

- **S3 Bucket ID**: Para subir tus logs
- **Lambda Function ARN**: Función de análisis
- **SNS Topic ARN**: Tópico de notificaciones

## 🛡️ Seguridad

### Permisos IAM

La función Lambda tiene permisos mínimos necesarios:
- Lectura de objetos S3 (solo del bucket de logs)
- Publicación en el tópico SNS específico
- Invocación del modelo Bedrock Claude 3 Haiku
- Escritura de logs de CloudWatch

### Mejores prácticas

- Los logs se procesan en memoria sin almacenamiento persistente
- Las credenciales se manejan automáticamente por IAM roles
- El análisis de IA se limita a 30 entradas por ejecución

## 💰 Costos estimados

- **Lambda**: ~$0.20 por millón de invocaciones
- **Bedrock**: ~$0.25 por 1K tokens (Claude 3 Haiku)
- **SNS**: ~$0.50 por millón de notificaciones
- **S3**: ~$0.023 por GB almacenado

## 🔍 Troubleshooting

### Lambda no se ejecuta
- Verifica que el bucket tenga el trigger configurado
- Revisa los logs de CloudWatch para errores

### No llegan emails
- Confirma la suscripción SNS en tu email
- Verifica que el email esté correctamente configurado

### Errores de Bedrock
- Asegúrate de tener acceso al modelo Claude 3 Haiku
- Verifica que la región sea compatible con Bedrock

## 🧹 Limpieza

Para eliminar todos los recursos:

```bash
terraform destroy
```

## 📝 Licencia

Este proyecto está bajo la licencia MIT.

**Nota**: Este sistema está diseñado para análisis de logs de portafolios y aplicaciones web. Para entornos de producción críticos, considera implementar análisis más robustos y almacenamiento de logs a largo plazo.

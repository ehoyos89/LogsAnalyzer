import boto3
import csv
import json
import io
import os

# Inicializar clientes de AWS
# Usamos variables de entorno para que sea configurable desde Terraform
bedrock = boto3.client(service_name='bedrock-runtime')
sns = boto3.client('sns')

def lambda_handler(event, context):
    # 1. Obtener información del evento de S3
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    topic_arn = os.environ.get('SNS_TOPIC_ARN')
    
    s3 = boto3.client('s3')
    
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        # Los logs de CloudFront a veces vienen comprimidos (.gz), 
        # pero si subes el .csv directamente, este decode funcionará:
        content = response['Body'].read().decode('utf-8')
        
        # 2. Procesar el CSV
        suspicious_logs = []
        # Importante: Los logs de CloudFront usan comas o tabuladores. 
        reader = csv.DictReader(io.StringIO(content))
        
        for row in reader:
            # Extraemos campos clave basados en el archivo de logs. 
            status = row.get('sc-status', '200')
            uri = row.get('cs-uri-stem', '')
            ip = row.get('c-ip', '0.0.0.0')
            user_agent = row.get('cs\\(User-Agent)', '')
            method = row.get('cs-method', '')

            # Lógica de detección:
            # Filtramos errores 403/404 o rutas sensibles: /.env, .php 
            is_error = int(status) >= 400
            is_sensitive_path = any(x in uri.lower() for x in ['.env', '.git', 'phpinfo', 'admin'])
            is_bot = "Assetnote" in user_agent or "Censys" in user_agent # Detectados en tus logs 

            if is_error or is_sensitive_path or is_bot:
                entry = f"MÉTODO: {method} | IP: {ip} | RUTA: {uri} | STATUS: {status} | AGENTE: {user_agent}"
                suspicious_logs.append(entry)

        if not suspicious_logs:
            print("No se detectó actividad sospechosa.")
            return

        # 3. Preparar el análisis para Amazon Bedrock
        # Tomamos una muestra para no exceder límites de tokens
        log_sample = "\n".join(suspicious_logs[:30])
        
        prompt = f"""
        Actúa como un experto en Seguridad en la Nube. He detectado actividad sospechosa en los logs de mi portafolio.
        Analiza estos eventos y dime:
        1. ¿Qué tipo de ataque o escaneo están intentando? (Ej: Directory Traversal, Brute Force, etc.)
        2. Identifica la IP más agresiva.
        3. Dame una recomendación técnica para mi WAF o configuración de servidor.

        LOGS A ANALIZAR:
        {log_sample}
        """

        # Configuración para Claude 3 Haiku
        native_request = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                }
            ],
        }

        response_bedrock = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps(native_request)
        )
        
        result = json.loads(response_bedrock.get('body').read())
        analysis_text = result['content'][0]['text']

        # 4. Notificar por SNS
        sns.publish(
            TopicArn=topic_arn,
            Subject="⚠️ Alerta de Seguridad Portafolio - Análisis IA",
            Message=f"Se han analizado logs sospechosos.\n\nResumen de la IA:\n{analysis_text}"
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        raise e
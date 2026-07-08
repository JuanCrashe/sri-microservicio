# Guía de Despliegue Automatizado en AWS (Amazon Web Services)

Este documento describe la estrategia de Infraestructura como Código (IaC) implementada para el microservicio SRI utilizando **Amazon EC2** y aprovisionamiento automático mediante `user-data`.

Esta solución garantiza que cada nueva instancia nazca con todo el stack de software configurado, sin necesidad de intervención manual.

> [!NOTE]
> **Contexto Académico (Cuentas de Estudiante)**
> Este despliegue fue diseñado y probado en un entorno de capa gratuita (Free Tier / AWS Educate). A diferencia de Microsoft Azure, AWS demostró mayor flexibilidad y disponibilidad de inventario físico para instancias gratuitas (`t2.micro`), permitiendo que la automatización por CLI (Infraestructura como Código) se ejecutara de principio a fin sin bloqueos por cuotas regionales o restricciones de capacidad.

## Requisitos Previos

- Tener una cuenta activa en AWS.
- Acceso a **AWS CloudShell** (la consola nativa web de AWS).
- El microservicio está diseñado para ser desplegado sobre la imagen oficial **Amazon Linux 2023**.

## Procedimiento de Despliegue

Para desplegar la infraestructura en la nube, se ha creado un script Bash automatizado que utiliza la AWS CLI. Este script realiza 4 tareas fundamentales:

1. **Gestión de Llaves:** Crea un Key Pair (`sri-key-pair`) para acceso SSH seguro.
2. **Seguridad Perimetral:** Aprovisiona un Security Group (`sri-security-group`) y habilita tráfico en los puertos `22` (SSH), `8080` (Frontend) y `5000` (Backend).
3. **Inyección de Configuración (User-Data):** Prepara un script que la máquina ejecutará como `root` durante su primer arranque. Este script se encarga de:
   - Instalar dependencias (Git, Docker, Docker Compose).
   - Clonar el repositorio desde GitHub.
   - Detectar la IP pública dinámicamente mediante `ifconfig.me`.
   - Generar el archivo `.env` de producción.
   - Levantar la arquitectura mediante `docker-compose up -d --build`.
4. **Lanzamiento de EC2:** Crea la instancia `t2.micro` vinculando todos los recursos anteriores.

### Ejecución del Script (AWS CloudShell)

Dado que AWS CloudShell ya posee credenciales administrativas, basta con crear un archivo en la terminal, pegar el siguiente código y ejecutarlo:

```bash
#!/bin/bash
# ==========================================
# SCRIPT DE DESPLIEGUE EN AWS (EC2)
# ==========================================

# Variables
REPO_URL="https://github.com/JuanCrashe/sri-microservicio.git"
KEY_NAME="sri-key-pair"
SG_NAME="sri-security-group"
AMI_ID="ami-053a45fff0a704a47" # Amazon Linux 2023 en us-east-1
INSTANCE_TYPE="t2.micro"

# 1. Crear Key Pair
rm -f $KEY_NAME.pem
aws ec2 create-key-pair --key-name $KEY_NAME --query 'KeyMaterial' --output text > $KEY_NAME.pem
chmod 400 $KEY_NAME.pem

# 2. Crear Security Group
SG_ID=$(aws ec2 create-security-group --group-name $SG_NAME --description "SG para Microservicio SRI" --query 'GroupId' --output text)
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0 > /dev/null
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 8080 --cidr 0.0.0.0/0 > /dev/null
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 5000 --cidr 0.0.0.0/0 > /dev/null

# 3. Preparar User Data
cat <<EOF > user_data.sh
#!/bin/bash
dnf update -y
dnf install -y git docker
systemctl start docker
systemctl enable docker
usermod -aG docker ec2-user
curl -L "https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clonar repo
sudo -u ec2-user git clone $REPO_URL /home/ec2-user/proyecto-sri
cd /home/ec2-user/proyecto-sri

# Capturar IP pública dinámicamente (IMDSv2 o curl)
PUBLIC_IP=\$(curl -s ifconfig.me)

# Inyectar variables de entorno (Reemplazar credenciales de Supabase)
cat <<EOT >> .env
SUPABASE_URL=<TU_URL_DE_SUPABASE>
SUPABASE_KEY=<TU_LLAVE_DE_SUPABASE>
JWT_SECRET=super-secret-key-cambiar-en-produccion
FLASK_SECRET_KEY=clave_secreta_frontend_aqui
PUBLIC_BACKEND_URL=http://\$PUBLIC_IP:5000
EOT

# Desplegar
/usr/local/bin/docker-compose up -d --build
EOF

# 4. Lanzar Instancia EC2
aws ec2 run-instances \
  --image-id $AMI_ID \
  --count 1 \
  --instance-type $INSTANCE_TYPE \
  --key-name $KEY_NAME \
  --security-group-ids $SG_ID \
  --user-data file://user_data.sh \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=SRI-Microservicio}]' \
  > /dev/null

# 5. Eliminar el script temporal
rm user_data.sh
```
*(Nota: Para replicar este despliegue, reemplace los valores de `SUPABASE_URL` y `SUPABASE_KEY` dentro de `user_data.sh` por sus credenciales legítimas de base de datos).*

## Validación
Al ejecutar el script, la consola devolverá la IP Pública asignada por Amazon. Espere entre 3 y 5 minutos para que la máquina virtual complete su proceso de inicialización en segundo plano. Luego, acceda mediante su navegador web al Frontend de la aplicación:

`http://<IP_PUBLICA_AWS>:8080`

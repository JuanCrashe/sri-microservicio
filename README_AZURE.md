# Guía de Despliegue en Microsoft Azure (Alternativa Gráfica)

Esta guía documenta la estrategia de despliegue utilizada en Azure para sortear las restricciones de cuota y disponibilidad física de servidores (Capacity Restrictions) inherentes a las cuentas de estudiante/gratuitas.

El despliegue sigue siendo automatizado a nivel de Sistema Operativo mediante la inyección de un script `cloud-init` (Custom Data).

## Pasos de Creación

1. Ingresar a [portal.azure.com](https://portal.azure.com).
2. Ir a **Virtual Machines** y seleccionar **Crear > Máquina virtual de Azure**.
3. **Configuración Básica:**
   - **Grupo de recursos:** `sri-rg-final`
   - **Nombre de la máquina:** `sri-vm-server`
   - **Región:** `Canada Central` (o cualquier región con inventario disponible).
   - **Imagen:** `Ubuntu Server 22.04 LTS`
   - **Tamaño:** `Standard_D2s_v3` (o la familia B si hay disponibilidad).
4. **Autenticación:**
   - Usuario: `azureuser`
   - Tipo: `Clave pública SSH` (Generar nuevo par de claves).
5. En la pestaña **Opciones Avanzadas**, ubicar la sección **Datos personalizados (Custom Data)** y pegar el siguiente script de aprovisionamiento:

```bash
#!/bin/bash
# 1. Actualizar e instalar dependencias
apt-get update -y
apt-get install -y ca-certificates curl gnupg git

# 2. Instalar Docker y Docker Compose desde repositorios estables de Ubuntu
apt-get install -y docker.io docker-compose

# 3. Iniciar Docker
systemctl enable docker
systemctl start docker
usermod -aG docker azureuser

# 4. Clonar el proyecto
cd /home/azureuser
git clone https://github.com/JuanCrashe/sri-microservicio.git proyecto-sri
cd proyecto-sri

# 5. Configurar Variables de Entorno
PUBLIC_IP=\$(curl -s ifconfig.me)

cat <<EOT > .env
SUPABASE_URL=<TU_URL_DE_SUPABASE>
SUPABASE_KEY=<TU_LLAVE_DE_SUPABASE>
JWT_SECRET=super-secret-key-cambiar-en-produccion
FLASK_SECRET_KEY=clave_secreta_frontend_aqui
PUBLIC_BACKEND_URL=http://\$PUBLIC_IP:5000
EOT

# 6. Construir y levantar contenedores
docker-compose up -d --build
```
*(Nota: Reemplaza `<TU_URL_DE_SUPABASE>` y `<TU_LLAVE_DE_SUPABASE>` por tus credenciales reales antes de pegar el script).*

6. Clic en **Revisar y crear**. Descargar la llave `.pem` cuando el portal lo solicite.
7. Una vez creada la máquina, ir al recurso, entrar a la sección **Redes** y abrir los puertos **8080** (Frontend) y **5000** (Backend).

## Acceso al Sistema
Una vez finalizado el aprovisionamiento interno (aprox. 4 minutos), el microservicio estará disponible en:
`http://<IP_PUBLICA_AZURE>:8080`

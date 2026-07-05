# Microservicio SRI - Gestión de Contribuyentes

Este proyecto forma parte de un Trabajo de Fin de Máster (TFM) para la **Maestría en DevOps de la UNIR**. Consiste en un microservicio web contenerizado que permite a los contribuyentes del Servicio de Rentas Internas (SRI) autenticarse y consultar su información registrada de forma segura.

## 🚀 Arquitectura y Tecnologías

El sistema sigue una arquitectura moderna, desacoplada y orientada a microservicios:

- **Frontend (Interfaz de Usuario):** Construido con Python (Flask), Jinja2 y **Tailwind CSS**. Actúa como capa de presentación, manejando las sesiones de usuario y consumiendo la API de forma asíncrona mediante Fetch API.
- **Backend (API REST):** Construido con Python (Flask). Expone endpoints protegidos por JWT (JSON Web Tokens). Es la única capa que tiene permisos para comunicarse con la base de datos.
- **Base de Datos (Persistencia):** Utiliza **Supabase (PostgreSQL)** en la nube para almacenar el estado y la información de los contribuyentes, enlazado directamente a través del SDK oficial de Python.
- **Orquestación y Contenedores:** Todo el ecosistema (Frontend y Backend) se encapsula en contenedores aislados mediante **Docker** y se gestiona con **Docker Compose**.
- **Infraestructura Cloud:** Preparado para un despliegue totalmente automatizado mediante scripts de *User Data* en **Amazon Web Services (AWS EC2)**.

## 📋 Requisitos Previos

Si deseas desplegar este proyecto en tu entorno local, necesitarás:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y corriendo.
- Una cuenta gratuita en [Supabase](https://supabase.com/) con un proyecto vacío.
- Git.

## ⚙️ Configuración del Entorno Local

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/TU_USUARIO/sri-microservicio.git
   cd sri-microservicio
   ```

2. **Configurar las variables de entorno:**
   Copia el archivo de ejemplo y configúralo con tus credenciales de Supabase.
   ```bash
   cp .env.example .env
   ```

3. **Ejecutar el script SQL en Supabase:**
   Desde el panel de "SQL Editor" de tu proyecto de Supabase, debes crear la tabla `contribuyentes` con un usuario administrador. (Puedes encontrar el script completo en la documentación de despliegue).

4. **Construir y Levantar los Contenedores:**
   ```bash
   docker-compose up -d --build
   ```

5. **Acceso a la Aplicación:**
   Abre tu navegador web y dirígete a: `http://localhost:8080`.

## ☁️ Despliegue en AWS (Amazon Web Services)

Este proyecto cuenta con soporte de infraestructura como código mediante scripts nativos de AWS CLI. 
En la documentación técnica generada (`guia_despliegue.md` y `despliegue_aws.sh`), se encuentra el flujo completo automatizado para provisionar:
- Security Groups.
- Key Pairs.
- Instancias EC2 configuradas con inyección dinámica del archivo `.env` y arranque automatizado de los contenedores Docker en la nube.

## 🔒 Seguridad Implementada

- Contraseñas almacenadas utilizando hashes robustos (`bcrypt`).
- Endpoints protegidos mediante tokens JWT.
- Variables sensibles aisladas mediante `.env` inyectadas en tiempo de despliegue.
- Validación estricta de formato en el Backend y Frontend (ej. RUC = 13 dígitos numéricos exactos).

---
*Desarrollado como prototipo funcional para la Maestría en DevOps y Cloud Computing - UNIR (2026).*

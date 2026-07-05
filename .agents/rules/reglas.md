---
trigger: always_on
---

Reglas de Desarrollo: Microservicio de Consulta y Actualización SRI
Este documento define las reglas de arquitectura, desarrollo, contenerización y UI/UX para el microservicio de gestión de contribuyentes del SRI. El sistema consume y actualiza la información directamente desde las tablas alojadas en la persistencia local de Supabase (PostgreSQL).

1. Estructura del Proyecto y Arquitectura
   El proyecto debe seguir un enfoque multi-contenedor desacoplado. El frontend nunca toca la base de datos directamente; toda comunicación con la persistencia se realiza a través de la API del Backend.

/sri-microservice
│
├── /backend
│ ├── app/
│ │ ├── **init**.py
│ │ ├── routes.py # Endpoints de API REST
│ │ ├── models.py # Esquemas/Modelos de base de datos
│ │ └── database.py # Configuración de la conexión a Supabase
│ ├── Dockerfile
│ └── requirements.txt
│
├── /frontend
│ ├── app/
│ │ ├── **init**.py
│ │ ├── routes.py # Rutas de vistas Flask e intercepción de sesiones
│ │ ├── templates/ # HTML (Login, Dashboard, Detalle Contribuyente)
│ │ └── static/ # CSS, JS (Peticiones Asíncronas)
│ ├── Dockerfile
│ └── requirements.txt
│
└── docker-compose.yml

2. Contenerización y Orquestación (Docker)
   Cada componente debe correr en un entorno aislado con configuraciones óptimas de producción y desarrollo local.

Backend (backend/Dockerfile)

FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/\*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]

Frontend (frontend/Dockerfile)

FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:create_app()"]

Orquestación Local (docker-compose.yml)
El contenedor de persistencia debe usar la imagen oficial postgres:15-alpine.

El contenedor de la base de datos debe incluir un healthcheck estricto que verifique la disponibilidad de Postgres (pg_isready).

Los contenedores de backend y frontend deben depender del estado saludable (service_healthy) de sus dependencias previas utilizando depends_on.

Mapear las variables de entorno necesarias (POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, BACKEND_URL) de forma segura sin exponer credenciales en el repositorio.

3. Backend (Python API)
   El backend expondrá servicios REST limpios utilizando tipos de datos estrictos (Type Hinting).

Endpoints Requeridos:

POST /api/v1/auth/login: Verifica las credenciales del usuario y retorna un token JWT.

GET /api/v1/contribuyente/<ruc>: Busca en la tabla de Supabase y retorna el objeto JSON con los datos del contribuyente (o 404 Not Found si no existe).

PUT /api/v1/contribuyente/<ruc>: Recibe un JSON, actualiza los campos permitidos del contribuyente en Supabase y actualiza automáticamente el campo ultima_actualizacion.

Seguridad:

Las rutas de contribuyentes deben estar protegidas. Exigir obligatoriamente el envío del token en las cabeceras HTTP (Authorization: Bearer <JWT_TOKEN>).

Validar sintácticamente el RUC (debe ser una cadena de 13 dígitos numéricos exactos) antes de ejecutar cualquier consulta en la base de datos.

4. Persistencia (Supabase / Postgres Estructura)
   Diseño relacional basado en las obligaciones y estructuras típicas de control fiscal.

Tabla usuarios:

id: UUID (Primary Key, autogenerado).

email: VARCHAR único.

password_hash: VARCHAR (Cifrado estrictamente con bcrypt o argon2).

Tabla contribuyentes:

ruc: VARCHAR(13) (Primary Key).

razon_social: VARCHAR.

estado_ruc: VARCHAR (ej. "ACTIVO", "SUSPENDIDO").

tipo_contribuyente: VARCHAR (ej. "Persona Natural", "Sociedad").

regimen_impositivo: VARCHAR (ej. "RIMPE - Emprendedor", "Régimen General").

actividad_economica: TEXT.

ultima_actualizacion: TIMESTAMP con zona horaria (se actualiza automáticamente en cada PUT).

5. Frontend (Flask) y Reglas UX/UI
   El frontend se encarga exclusivamente de renderizar las vistas, gestionar la sesión del usuario (vía cookies/session de Flask) y consumir asíncronamente la API del Backend.

Seguridad y Flujo de Sesión

- Pantalla de Login: Es la página raíz (/). No se puede acceder a ninguna otra pantalla sin autenticación. Si el backend valida con éxito las credenciales, el Frontend almacena el JWT en la sesión segura de Flask.

- Middlewares de Ruta: Implementar un decorador @login_required en Flask para redirigir al /login a cualquier usuario no autenticado.

Reglas de Diseño y Experiencia de Usuario (UX/UI)

- Framework Estético: Utilizar Tailwind CSS o Bootstrap 5 con un enfoque limpio e institucional (paleta de colores azul corporativo, gris claro para fondos y blanco para contenedores).

- Validación en Cliente (Frontend): El campo de búsqueda de RUC debe tener una máscara de entrada o validación HTML/JS que solo permita números y limite la longitud a 13 caracteres exactos, deshabilitando el botón de envío si la regla no se cumple.

- Interacciones Asíncronas (AJAX / Fetch API): La consulta y la actualización de datos deben ejecutarse en segundo plano sin recargar toda la página web.

- Estados de Carga Inmediatos: Al presionar "Buscar" o "Actualizar", el botón debe cambiar a un estado deshabilitado mostrando un spinner de carga para evitar clics duplicados y dar feedback de que el sistema está trabajando.

- Mensajes de Confirmación Dinámicos: Utilizar componentes de notificación efímeros (Toasts) o alertas de color verde para actualizaciones exitosas y rojo para errores (ej. "El RUC ingresado no se encuentra registrado").

- Diseño de Formulario de Actualización: Los datos del contribuyente deben mostrarse organizados en tarjetas (Cards). El RUC debe ser un campo de solo lectura (readonly), permitiendo modificar únicamente los campos editables definidos.

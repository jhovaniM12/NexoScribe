# NexoScribe Backend

Backend de NexoScribe construido con FastAPI, SQLAlchemy, Alembic y PostgreSQL.

El proyecto sigue una arquitectura por capas para separar rutas HTTP, validaciones, logica de negocio, acceso a datos, configuracion y utilidades compartidas.

## Estado actual

Actualmente el backend tiene configurado:

- Aplicacion FastAPI base.
- Ruta de salud: `GET /api/v1/health`.
- Configuracion con `pydantic-settings` y archivo `.env`.
- Conexion a PostgreSQL/Neon con SQLAlchemy.
- Modelos iniciales: `User`, `Workspace` y `WorkspaceMember`.
- Seguridad basica para hash y verificacion de passwords con `passlib` + `bcrypt`.
- Modulo inicial `auth` con schemas, repository y service para registro.
- Alembic configurado para leer la URL de base de datos desde `.env`.
- Migracion baseline vacia para sincronizar Alembic con el schema existente en Neon.

## Stack

- Python 3.12
- FastAPI
- Uvicorn
- Pydantic v2
- Pydantic Settings
- SQLAlchemy 2
- Alembic
- PostgreSQL en Neon
- psycopg 3
- python-jose
- passlib + bcrypt
- pytest
- ruff
- mypy

## Estructura

```text
backend/
|-- alembic/
|   |-- versions/
|   |   `-- a4aab67fd70b_baseline_existing_schema.py
|   |-- env.py
|   `-- script.py.mako
|-- app/
|   |-- main.py
|   |-- core/
|   |   |-- config.py
|   |   |-- database.py
|   |   `-- security.py
|   |-- models/
|   |   |-- __init__.py
|   |   |-- enums.py
|   |   |-- user.py
|   |   `-- workspace.py
|   |-- modules/
|   |   `-- auth/
|   |       |-- router.py
|   |       |-- schemas.py
|   |       |-- service.py
|   |       `-- repository.py
|   `-- shared/
|       `-- responses.py
|-- .env
|-- alembic.ini
|-- requirements.txt
`-- nexoscribe_api_endpoints_documentation.md
```

## Capas del proyecto

### `app/main.py`

Punto de entrada de FastAPI. Aqui se crea la instancia principal de la aplicacion y se registran rutas globales.

Actualmente expone:

```http
GET /api/v1/health
```

### `app/core/`

Contiene configuracion y piezas transversales del backend.

- `config.py`: carga variables desde `.env`.
- `database.py`: configura SQLAlchemy, `engine`, `SessionLocal`, `Base` y `get_db`.
- `security.py`: contiene funciones para hashear y verificar passwords.

### `app/models/`

Contiene los modelos SQLAlchemy.

Modelos actuales:

- `User`
- `Workspace`
- `WorkspaceMember`

Enums actuales:

- `WorkspaceMemberRole`
- `WorkspaceMemberStatus`

### `app/modules/`

Contiene los modulos funcionales del negocio.

Cada modulo debe seguir esta separacion:

```text
router.py      # endpoints HTTP
schemas.py     # modelos Pydantic de entrada/salida
service.py     # logica de negocio
repository.py  # acceso a base de datos
```

Modulo actual:

```text
app/modules/auth/
```

### `app/shared/`

Espacio para utilidades compartidas, por ejemplo respuestas estandar, paginacion y excepciones.

## Variables de entorno

Crear un archivo `.env` en la raiz del backend.

Ejemplo:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require&channel_binding=require
```

Para Neon, la URL original suele venir como:

```text
postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
```

En este proyecto debe usarse con el driver de SQLAlchemy + psycopg:

```text
postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require
```

## Instalacion

Desde la carpeta `backend`:

```powershell
python -m venv .venv
```

Activar el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias:

```powershell
pip install -r requirements.txt
```

## Ejecutar el servidor

```powershell
uvicorn app.main:app --reload
```

La API queda disponible en:

```text
http://127.0.0.1:8000
```

Documentacion interactiva:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/api/v1/health
```

Respuesta esperada:

```json
{
  "status": "ok"
}
```

## Base de datos

El proyecto usa SQLAlchemy con sesiones sincronas.

La configuracion principal esta en:

```text
app/core/database.py
```

Piezas importantes:

- `engine`: conexion principal hacia PostgreSQL.
- `SessionLocal`: fabrica de sesiones.
- `Base`: clase base para los modelos SQLAlchemy.
- `get_db`: dependencia para inyectar una sesion en endpoints.

## Alembic

Alembic esta configurado para leer `DATABASE_URL` desde `.env`.

Archivo principal:

```text
alembic/env.py
```

El proyecto ya tiene una migracion baseline vacia:

```text
alembic/versions/a4aab67fd70b_baseline_existing_schema.py
```

Esta migracion no crea tablas. Solo sirve como punto inicial porque las tablas existentes fueron creadas directamente en Neon.

Ver estado actual:

```powershell
.\.venv\Scripts\alembic.exe current
```

Crear una nueva migracion cuando cambien los modelos:

```powershell
.\.venv\Scripts\alembic.exe revision --autogenerate -m "describe change"
```

Aplicar migraciones:

```powershell
.\.venv\Scripts\alembic.exe upgrade head
```

## Flujo de desarrollo recomendado

Para construir un endpoint:

1. Definir schemas en `schemas.py`.
2. Crear funciones de consulta/escritura en `repository.py`.
3. Crear la logica de negocio en `service.py`.
4. Exponer la ruta en `router.py`.
5. Registrar el router en `app/main.py`.
6. Probar manualmente en `/docs`.
7. Agregar tests cuando el flujo sea estable.

Ejemplo para auth:

```text
app/modules/auth/schemas.py
app/modules/auth/repository.py
app/modules/auth/service.py
app/modules/auth/router.py
```

## Convencion de respuestas

La documentacion base del producto propone respuestas con este formato:

Respuesta exitosa:

```json
{
  "success": true,
  "data": {}
}
```

Respuesta de error:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Descripcion del error"
  }
}
```

Esta convencion deberia implementarse en `app/shared/responses.py` y `app/shared/exceptions.py`.

## Endpoints planeados

La documentacion completa de endpoints esta en:

```text
nexoscribe_api_endpoints_documentation.md
```

Modulos planeados para el MVP:

- Auth
- Users
- Workspaces
- Workspace members
- Spaces
- Projects
- Tasks
- Task comments
- Task attachments
- Notes
- Publications
- Publication channels
- Social platforms
- Calendar
- Reminders
- Google Calendar integrations
- Dashboard

## Siguiente paso

El siguiente paso tecnico recomendado es completar el endpoint:

```http
POST /api/v1/auth/register
```

Ese flujo debe:

1. Recibir `name`, `email` y `password`.
2. Validar si el email ya existe.
3. Hashear el password.
4. Crear el usuario.
5. Crear su workspace personal.
6. Crear su membresia como `owner`.
7. Devolver el usuario sin exponer `hashed_password`.

Despues de eso se pueden agregar cookies HTTP-only con access token y refresh token.

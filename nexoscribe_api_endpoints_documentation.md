# nexoScribe - Documentación Base de Endpoints API

# Introducción

Esta documentación describe los endpoints principales para el MVP de nexoScribe.

La plataforma está diseñada como un sistema colaborativo tipo Asana/Notion enfocado en:

- Gestión de tareas
- Cronograma de publicaciones
- Colaboración en equipo
- Gestión de contenido
- Integración con Google Calendar
- Organización por workspaces

---

# Reglas Generales

## Autenticación

La autenticación se maneja mediante cookies HTTP-only.

El frontend NO almacena tokens en:

- localStorage
- sessionStorage

El backend retorna cookies seguras utilizando:

```http
Set-Cookie
```

Todas las peticiones autenticadas deben enviarse con credenciales.

## Frontend

### Fetch API

```ts
fetch('/api/v1/auth/me', {
  credentials: 'include'
})
```

### Axios

```ts
axios.get('/api/v1/auth/me', {
  withCredentials: true
})
```

## Cookies utilizadas

### access_token

Cookie de acceso de corta duración.

Ejemplo:

```http
Set-Cookie: access_token=<jwt>; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=900
```

### refresh_token

Cookie utilizada para renovar la sesión.

Ejemplo:

```http
Set-Cookie: refresh_token=<jwt>; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=604800
```

## Seguridad

Las cookies deben utilizar:

- HttpOnly
- Secure
- SameSite=Lax o Strict

Esto evita exposición del token mediante JavaScript y reduce riesgos XSS.


---

## Multi-tenant

Toda la información pertenece a un `workspace`.

Un usuario:

- Puede pertenecer máximo a 2 workspaces
- Tiene un workspace personal automático

---

## Convenciones

## Base URL

```http
/api/v1
```

---

## Formato de respuestas

### Success

```json
{
  "success": true,
  "data": {}
}
```

### Error

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Descripción del error"
  }
}
```

---

# 1. AUTH

# POST /auth/register

## Descripción

Registra un nuevo usuario.

Al registrarse:

- Se crea automáticamente un workspace personal
- El usuario queda autenticado

## Body

```json
{
  "name": "Jhovani",
  "email": "jhovani@email.com",
  "password": "123456"
}
```

## Cookies generadas

```http
Set-Cookie: access_token=<jwt>; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=900
```

```http
Set-Cookie: refresh_token=<jwt>; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=604800
```

## Response

```json
{
  "success": true,
  "data": {
    "user": {}
  }
}
```

---

# POST /auth/login

## Descripción

Inicia sesión.

Al autenticarse correctamente:

- Se genera un access token
- Se genera un refresh token
- Ambos tokens se almacenan en cookies HTTP-only

## Body

```json
{
  "email": "jhovani@email.com",
  "password": "123456"
}
```

## Cookies generadas

```http
Set-Cookie: access_token=<jwt>; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=900
```

```http
Set-Cookie: refresh_token=<jwt>; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=604800
```

## Response

```json
{
  "success": true,
  "data": {
    "user": {}
  }
}
```

---

# POST /auth/refresh

## Descripción

Renueva el access token utilizando el refresh token.

## Requiere

Cookie:

```http
refresh_token
```

## Response

```http
Set-Cookie: access_token=<jwt>
```

```json
{
  "success": true
}
```

---

# POST /auth/logout

## Descripción

Cierra sesión del usuario actual.

---

# POST /auth/forgot-password

## Descripción

Solicita el restablecimiento de contraseña para un usuario registrado.

Si el email existe, el backend genera un token temporal de recuperación y envía un enlace al correo del usuario.

Por seguridad, la respuesta debe ser la misma aunque el email no exista.

## Body

```json
{
  "email": "jhovani@email.com"
}
```

## Response

```json
{
  "success": true,
  "message": "If the email exists, a password reset link has been sent"
}
```

---

# POST /auth/reset-password

## Descripción

Restablece la contraseña utilizando un token temporal enviado por correo.

El token debe ser de corta duración y de un solo uso.

## Body

```json
{
  "token": "reset_token",
  "password": "nuevaPassword123"
}
```

## Response

```json
{
  "success": true
}
```

## Errores posibles

```json
{
  "success": false,
  "error": {
    "code": "INVALID_RESET_TOKEN",
    "message": "Invalid or expired reset token"
  }
}
```

---

# GET /auth/me

## Descripción

Obtiene el usuario autenticado.

---

# PATCH /users/me

## Descripción

Actualiza el perfil del usuario.

## Body

```json
{
  "name": "Nuevo nombre",
  "imageUrl": "https://..."
}
```

---

# PATCH /users/me/password

## Descripción

Actualiza la contraseña.

## Body

```json
{
  "currentPassword": "123456",
  "newPassword": "abcdef"
}
```

---

# 2. WORKSPACES

# GET /workspaces

## Descripción

Obtiene los workspaces del usuario.

---

# POST /workspaces

## Descripción

Crea un nuevo workspace.

## Restricción

Un usuario solo puede pertenecer máximo a 2 workspaces.

## Body

```json
{
  "name": "Agencia Creativa",
  "slug": "agencia-creativa",
  "type": "team"
}
```

## Errores posibles

```json
{
  "success": false,
  "error": {
    "code": "WORKSPACE_LIMIT_REACHED",
    "message": "Solo puedes tener máximo 2 workspaces"
  }
}
```

---

# GET /workspaces/:workspaceId

## Descripción

Obtiene detalle de un workspace.

---

# PATCH /workspaces/:workspaceId

## Descripción

Actualiza un workspace.

---

# DELETE /workspaces/:workspaceId

## Descripción

Elimina un workspace.

---

# 3. WORKSPACE MEMBERS

# GET /workspaces/:workspaceId/members

## Descripción

Lista los miembros del workspace.

---

# POST /workspaces/:workspaceId/members/invite

## Descripción

Invita un usuario al workspace.

## Body

```json
{
  "email": "usuario@email.com",
  "role": "member"
}
```

---

# PATCH /workspaces/:workspaceId/members/:memberId/role

## Descripción

Actualiza el rol del miembro.

---

# PATCH /workspaces/:workspaceId/members/:memberId/status

## Descripción

Actualiza el estado del miembro.

---

# DELETE /workspaces/:workspaceId/members/:memberId

## Descripción

Remueve un miembro del workspace.

---

# 4. SPACES

# GET /workspaces/:workspaceId/spaces

## Descripción

Lista los espacios del workspace.

---

# POST /workspaces/:workspaceId/spaces

## Descripción

Crea un espacio.

## Body

```json
{
  "name": "Marketing",
  "description": "Equipo de marketing"
}
```

---

# GET /workspaces/:workspaceId/spaces/:spaceId

## Descripción

Obtiene detalle de un espacio.

---

# PATCH /workspaces/:workspaceId/spaces/:spaceId

## Descripción

Actualiza un espacio.

---

# DELETE /workspaces/:workspaceId/spaces/:spaceId

## Descripción

Elimina un espacio.

---

# 5. PROJECTS

# GET /workspaces/:workspaceId/projects

## Descripción

Lista proyectos.

## Query params

```http
?spaceId=
?status=
```

---

# POST /workspaces/:workspaceId/projects

## Descripción

Crea un proyecto.

## Body

```json
{
  "spaceId": "uuid",
  "name": "Campaña Mayo",
  "description": "Contenido para mayo"
}
```

---

# GET /workspaces/:workspaceId/projects/:projectId

## Descripción

Obtiene detalle de un proyecto.

---

# PATCH /workspaces/:workspaceId/projects/:projectId

## Descripción

Actualiza un proyecto.

---

# DELETE /workspaces/:workspaceId/projects/:projectId

## Descripción

Elimina un proyecto.

---

# 6. TASKS

# GET /workspaces/:workspaceId/tasks

## Descripción

Lista tareas.

## Query params

```http
?spaceId=
?projectId=
?assigneeId=
?status=
?type=
?dueFrom=
?dueTo=
```

---

# POST /workspaces/:workspaceId/tasks

## Descripción

Crea una tarea.

## Body

```json
{
  "spaceId": "uuid",
  "projectId": "uuid",
  "title": "Diseñar portada",
  "description": "Crear portada del reel",
  "type": "general",
  "status": "todo",
  "priority": "high",
  "assigneeId": "uuid",
  "dueDate": "2026-05-20"
}
```

## Crear subtarea

```json
{
  "parentTaskId": "uuid"
}
```

---

# GET /workspaces/:workspaceId/tasks/:taskId

## Descripción

Obtiene detalle de una tarea.

---

# PATCH /workspaces/:workspaceId/tasks/:taskId

## Descripción

Actualiza una tarea.

---

# DELETE /workspaces/:workspaceId/tasks/:taskId

## Descripción

Elimina una tarea.

---

# GET /workspaces/:workspaceId/tasks/:taskId/subtasks

## Descripción

Obtiene las subtareas de una tarea.

---

# POST /workspaces/:workspaceId/tasks/:taskId/subtasks

## Descripción

Crea una subtarea.

---

# 7. TASK COMMENTS

# GET /workspaces/:workspaceId/tasks/:taskId/comments

## Descripción

Lista comentarios de una tarea.

---

# POST /workspaces/:workspaceId/tasks/:taskId/comments

## Descripción

Crea un comentario.

## Body

```json
{
  "content": "Ya quedó lista la portada"
}
```

## Responder comentario

```json
{
  "content": "Perfecto",
  "parentCommentId": "uuid"
}
```

---

# PATCH /workspaces/:workspaceId/tasks/:taskId/comments/:commentId

## Descripción

Actualiza un comentario.

---

# DELETE /workspaces/:workspaceId/tasks/:taskId/comments/:commentId

## Descripción

Elimina un comentario.

---

# 8. TASK ATTACHMENTS

# GET /workspaces/:workspaceId/tasks/:taskId/attachments

## Descripción

Lista adjuntos de una tarea.

---

# POST /workspaces/:workspaceId/tasks/:taskId/attachments

## Descripción

Sube un adjunto.

## Tipos soportados

- Documentos
- Imágenes
- Videos
- Diseños

---

# DELETE /workspaces/:workspaceId/tasks/:taskId/attachments/:attachmentId

## Descripción

Elimina un adjunto.

---

# POST /workspaces/:workspaceId/uploads/presigned-url

## Descripción

Genera URL firmada para subida directa a storage.

---

# 9. NOTES

# GET /workspaces/:workspaceId/notes

## Descripción

Lista notas.

## Query params

```http
?spaceId=
?projectId=
?visibility=
?search=
```

---

# POST /workspaces/:workspaceId/notes

## Descripción

Crea una nota.

## Body

```json
{
  "title": "Ideas Instagram",
  "content": {},
  "spaceId": "uuid"
}
```

---

# GET /workspaces/:workspaceId/notes/:noteId

## Descripción

Obtiene detalle de una nota.

---

# PATCH /workspaces/:workspaceId/notes/:noteId

## Descripción

Actualiza una nota.

---

# DELETE /workspaces/:workspaceId/notes/:noteId

## Descripción

Elimina una nota.

---

# 10. PUBLICATIONS

# GET /workspaces/:workspaceId/publications

## Descripción

Lista publicaciones.

## Query params

```http
?platformId=
?status=
?from=
?to=
?assigneeId=
```

---

# POST /workspaces/:workspaceId/publications

## Descripción

Crea una publicación.

Internamente crea:

- task
- task_publication
- publication_channels

## Body

```json
{
  "spaceId": "uuid",
  "projectId": "uuid",
  "title": "Lanzamiento Reel",
  "description": "Contenido campaña",
  "content": "Copy principal",
  "priority": "high",
  "assigneeId": "uuid",
  "channels": [
    {
      "platformId": "instagram-id",
      "publishAt": "2026-05-20T10:00:00"
    },
    {
      "platformId": "tiktok-id",
      "publishAt": "2026-05-20T12:00:00"
    }
  ]
}
```

---

# GET /workspaces/:workspaceId/publications/:taskId

## Descripción

Obtiene detalle de una publicación.

---

# PATCH /workspaces/:workspaceId/publications/:taskId

## Descripción

Actualiza una publicación.

---

# DELETE /workspaces/:workspaceId/publications/:taskId

## Descripción

Elimina una publicación.

---

# 11. PUBLICATION CHANNELS

# GET /workspaces/:workspaceId/publications/:taskId/channels

## Descripción

Lista canales/redes sociales asociados a la publicación.

---

# POST /workspaces/:workspaceId/publications/:taskId/channels

## Descripción

Agrega un canal/red social.

---

# PATCH /workspaces/:workspaceId/publications/:taskId/channels/:channelId

## Descripción

Actualiza un canal.

---

# DELETE /workspaces/:workspaceId/publications/:taskId/channels/:channelId

## Descripción

Elimina un canal.

---

# 12. SOCIAL PLATFORMS

# GET /social-platforms

## Descripción

Lista las redes sociales disponibles.

## Response ejemplo

```json
[
  {
    "id": "uuid",
    "name": "Instagram",
    "slug": "instagram"
  }
]
```

---

# 13. CALENDAR

# GET /workspaces/:workspaceId/calendar/publications

## Descripción

Obtiene publicaciones para visualización en calendario.

## Query params

```http
?from=
?to=
?platformId=
?status=
```

---

# 14. REMINDERS

# GET /workspaces/:workspaceId/reminders

## Descripción

Lista recordatorios.

---

# POST /workspaces/:workspaceId/reminders

## Descripción

Crea un recordatorio.

## Body

```json
{
  "taskPublicationChannelId": "uuid",
  "remindAt": "2026-05-20T09:00:00",
  "channel": "push"
}
```

---

# PATCH /workspaces/:workspaceId/reminders/:reminderId

## Descripción

Actualiza un recordatorio.

---

# DELETE /workspaces/:workspaceId/reminders/:reminderId

## Descripción

Elimina un recordatorio.

---

# 15. GOOGLE CALENDAR

# GET /workspaces/:workspaceId/calendar-integrations

## Descripción

Lista integraciones de calendario.

---

# POST /workspaces/:workspaceId/calendar-integrations/google/connect

## Descripción

Conecta Google Calendar mediante OAuth.

---

# DELETE /workspaces/:workspaceId/calendar-integrations/:integrationId

## Descripción

Desconecta Google Calendar.

---

# POST /workspaces/:workspaceId/publications/:taskId/channels/:channelId/sync/google-calendar

## Descripción

Sincroniza una publicación con Google Calendar.

---

# DELETE /workspaces/:workspaceId/publications/:taskId/channels/:channelId/sync/google-calendar

## Descripción

Elimina sincronización con Google Calendar.

---

# 16. DASHBOARD

# GET /workspaces/:workspaceId/dashboard/summary

## Descripción

Obtiene resumen general del workspace.

## Información sugerida

- Tareas pendientes
- Publicaciones programadas
- Publicaciones por red social
- Próximas publicaciones
- Publicaciones vencidas
- Tareas asignadas al usuario
- Próximos recordatorios

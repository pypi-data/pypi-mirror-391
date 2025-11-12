# Servidor MCP para RhodeCode

Servidor MCP (Model Context Protocol) que proporciona herramientas para interactuar con la API de RhodeCode.

## Configuración

### Variables de Entorno

Antes de ejecutar el servidor, configura las siguientes variables de entorno:

```bash
# Windows PowerShell
$env:RC_API_URL = "https://tu-instancia.rhodecode.com/_admin/api"
$env:RC_API_TOKEN = "tu_token_de_autenticacion"
$env:RC_TIMEOUT_MS = "8000"  # Opcional, default: 8000
```

```bash
# Linux/macOS
export RC_API_URL="https://tu-instancia.rhodecode.com/_admin/api"
export RC_API_TOKEN="tu_token_de_autenticacion"
export RC_TIMEOUT_MS="8000"  # Opcional, default: 8000
```

### Instalación de Dependencias

Crea un entorno virtual e instala las dependencias:

```powershell
# Crear entorno virtual
py -3 -m venv .venv

# Activar entorno virtual (PowerShell)
. .\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install fastmcp requests
```

## Ejecución

```powershell
python MCPserver.py
```

El servidor se iniciará en `http://0.0.0.0:8000`

## Pruebas con Cliente

Se incluye un cliente de prueba (`client.py`) para verificar que todas las herramientas funcionen:

```powershell
# Pruebas básicas
python client.py

# Pruebas completas con un repositorio existente
python client.py --repo mi-repositorio

# Ver todas las opciones
python client.py --help
```

Consulta [CLIENT_README.md](CLIENT_README.md) para más detalles sobre el cliente de pruebas.

## Herramientas Implementadas

### Gestión de Repositorios

#### 1. `get_repos`
Obtiene la lista de todos los repositorios con filtros opcionales.

**Parámetros:**
- `root` (string, opcional): Nombre del grupo raíz para filtrar
- `traverse` (boolean, opcional): Si atravesar subgrupos (default: True)

**Ejemplo de uso:**
```json
{
  "root": "proyecto-x",
  "traverse": true
}
```

#### 2. `get_repo`
Obtiene información detallada de un repositorio específico.

**Parámetros:**
- `repoid` (string, requerido): Nombre o ID del repositorio
- `cache` (boolean, opcional): Usar caché (default: True)

**Ejemplo:**
```json
{
  "repoid": "mi-repositorio"
}
```

#### 3. `create_repo`
Crea un nuevo repositorio.

**Parámetros requeridos:**
- `repo_name` (string): Nombre del repositorio (puede incluir grupos con `/`)
- `repo_type` (string): Tipo de repo: `hg`, `git`, o `svn`

**Parámetros opcionales:**
- `owner` (string): Usuario propietario
- `description` (string): Descripción
- `private` (boolean): Si es privado
- `clone_uri` (string): URI para clonar
- `push_uri` (string): URI para push
- `landing_rev` (string): Revisión de aterrizaje (ej: `branch:default`)
- `enable_statistics` (boolean)
- `enable_locking` (boolean)
- `enable_downloads` (boolean)
- `copy_permissions` (boolean)

**Ejemplo:**
```json
{
  "repo_name": "proyectos/mi-nuevo-repo",
  "repo_type": "git",
  "description": "Mi nuevo repositorio",
  "private": true
}
```

#### 4. `update_repo`
Actualiza la configuración de un repositorio existente.

**Parámetros:**
- `repoid` (string, requerido): Nombre o ID del repositorio
- Todos los parámetros de `create_repo` son opcionales para actualizar

**Ejemplo:**
```json
{
  "repoid": "mi-repositorio",
  "description": "Nueva descripción",
  "private": false
}
```

#### 5. `delete_repo`
Elimina un repositorio.

**Parámetros:**
- `repoid` (string, requerido): Nombre o ID del repositorio
- `forks` (string, opcional): `detach` o `delete` para manejar forks

**Ejemplo:**
```json
{
  "repoid": "repo-obsoleto",
  "forks": "detach"
}
```

#### 6. `fork_repo`
Crea un fork de un repositorio existente.

**Parámetros requeridos:**
- `repoid` (string): Repositorio a bifurcar
- `fork_name` (string): Nombre del fork

**Parámetros opcionales:**
- `owner`, `description`, `private`, `clone_uri`, `landing_rev`, `copy_permissions`

**Ejemplo:**
```json
{
  "repoid": "repositorio-original",
  "fork_name": "mi-fork/repositorio-fork",
  "description": "Mi fork para desarrollo"
}
```

### Información de Repositorios

#### 7. `get_repo_refs`
Obtiene branches, tags, bookmarks del repositorio.

**Parámetros:**
- `repoid` (string, requerido)

**Retorna:**
- `bookmarks`: Diccionario de bookmarks
- `branches`: Diccionario de branches
- `branches_closed`: Branches cerradas
- `tags`: Diccionario de tags

#### 8. `get_repo_nodes`
Lista archivos y directorios en una ruta específica.

**Parámetros:**
- `repoid` (string, requerido)
- `revision` (string, requerido): Revisión (ej: `tip`, hash, branch)
- `root_path` (string, requerido): Ruta (ej: `/`, `src/`)
- `ret_type` (string, opcional): `all`, `files`, `dirs`
- `details` (string, opcional): `basic`, `full`
- `max_file_bytes` (integer, opcional)

#### 9. `get_repo_file`
Obtiene el contenido de un archivo específico.

**Parámetros:**
- `repoid` (string, requerido)
- `commit_id` (string, requerido)
- `file_path` (string, requerido)
- `max_file_bytes` (integer, opcional)
- `details` (string, opcional): `minimal`, `basic`, `full`
- `cache` (boolean, opcional)

#### 10. `get_repo_changeset`
Información de un commit específico.

**Parámetros:**
- `repoid` (string, requerido)
- `revision` (string, requerido)
- `details` (string, opcional): `basic`, `extended`, `full`

#### 11. `get_repo_changesets`
Obtiene un conjunto de commits.

**Parámetros:**
- `repoid` (string, requerido)
- `start_rev` (string, requerido)
- `limit` (integer, requerido)
- `details` (string, opcional): `basic`, `extended`, `full`

### Operaciones de Repositorio

#### 12. `invalidate_cache`
Invalida el caché de un repositorio.

**Parámetros:**
- `repoid` (string, requerido)
- `delete_keys` (boolean, opcional): Eliminar claves (default: False)

#### 13. `lock_repo`
Bloquea o desbloquea un repositorio.

**Parámetros:**
- `repoid` (string, requerido)
- `locked` (boolean, opcional): True para bloquear, False para desbloquear
- `userid` (string, opcional): Usuario que establece el bloqueo

**Sin especificar `locked`, muestra el estado actual del bloqueo.**

#### 14. `pull_repo`
Ejecuta pull desde una ubicación remota.

**Parámetros:**
- `repoid` (string, requerido)
- `remote_uri` (string, opcional): URI remota

#### 15. `maintenance`
Ejecuta tareas de mantenimiento en el repositorio.

**Parámetros:**
- `repoid` (string, requerido)

### Pull Requests

#### 16. `create_pr`
Crea un Pull Request.

**Parámetros:**
- `repo_name` (string, requerido)
- `source_ref` (string, requerido)
- `target_ref` (string, requerido)
- `title` (string, requerido)
- `description` (string, opcional)

## Recursos

### `repos_list`
Resource que proporciona una lista normalizada de repositorios.

## Estructura del Proyecto

```
MCPRhodecode/
├── MCPserver.py          # Servidor MCP principal
├── client.py             # Cliente de prueba
├── README.md             # Esta documentación
├── CLIENT_README.md      # Documentación del cliente
├── RESUMEN.md            # Resumen de implementación
├── ejemplos_uso.py       # Ejemplos de uso de las tools
├── requirements.txt      # Dependencias Python
├── .env.example          # Plantilla de configuración
├── .gitignore            # Exclusiones Git
└── .venv/                # Entorno virtual (no incluir en git)
```

## Notas Importantes

1. **Autenticación**: Necesitas un token de autenticación válido de RhodeCode con permisos adecuados.

2. **Permisos**: Cada operación requiere permisos específicos:
   - Lectura de repos: permisos de lectura
   - Crear repos: permisos de creación
   - Eliminar/actualizar: permisos de admin en el repo
   - Fork: permisos de lectura en el repo original

3. **Grupos de repositorios**: Puedes usar `/` en los nombres para crear repos dentro de grupos:
   - `mi-proyecto/backend/api` creará el repo `api` dentro de `mi-proyecto/backend`
   - Necesitas permisos de escritura en el último grupo

4. **Tareas asíncronas**: Algunas operaciones (como `create_repo`, `fork_repo`) pueden ejecutarse de forma asíncrona y retornar un `task` ID.

## Referencias

- [Documentación API RhodeCode](https://docs.rhodecode.com/4.x/rce/api/api.html)
- [Métodos de Repositorio](https://docs.rhodecode.com/4.x/rce/api/methods/repo-methods.html)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

## Licencia

Este proyecto es de código abierto. Úsalo según tus necesidades.

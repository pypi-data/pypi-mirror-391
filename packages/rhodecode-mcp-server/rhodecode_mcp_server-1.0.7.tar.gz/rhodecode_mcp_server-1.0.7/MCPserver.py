import os
import json
import uuid
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv  # Necesario para leer variables .env
import requests
from fastmcp import FastMCP

# Desactivar advertencias de SSL
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Desactivar advertencias de SSL también en requests
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# ---------- Configuración ----------
load_dotenv()  # Carga variables desde .env
RC_API_URL = os.getenv("RC_API_URL", "").strip()
RC_API_TOKEN = os.getenv("RC_API_TOKEN", "")
RC_TIMEOUT_MS = int(os.getenv("RC_TIMEOUT_MS", "8000"))
RC_READONLY = os.getenv("RC_READONLY", "false").lower() in ("true", "1", "yes")
RC_VERIFY_SSL = os.getenv("RC_VERIFY_SSL", "false").lower() in ("true", "1", "yes")
RC_CERT_PATH = os.getenv("RC_CERT_PATH", "").strip()  # Path a certificado personalizado (ej: auto-firmado)

_config_validated = False

def _validate_config():
    """Valida la configuración requerida. Se ejecuta solo cuando se inicia el servidor."""
    global _config_validated
    if _config_validated:
        return
    if not RC_API_URL or not RC_API_TOKEN:
        raise RuntimeError("Configura RC_API_URL y RC_API_TOKEN en variables de entorno.")
    
    # Validar certificado si está configurado
    if RC_CERT_PATH:
        if not os.path.exists(RC_CERT_PATH):
            raise RuntimeError(f"Certificado no encontrado en: {RC_CERT_PATH}")
        if os.path.getsize(RC_CERT_PATH) == 0:
            raise RuntimeError(f"Certificado vacío en: {RC_CERT_PATH}")
    
    _config_validated = True

HEADERS = {"Content-Type": "application/json"}

def check_readonly(operation: str) -> None:
    """
    Verifica si el servidor está en modo readonly.
    Si lo está, lanza una excepción para operaciones destructivas.
    """
    if RC_READONLY:
        raise RuntimeError(f"Operación '{operation}' bloqueada: servidor en modo READONLY")

def rc_jsonrpc(method: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Envía una petición JSON-RPC a RhodeCode con el esquema:
    {
      "id": "<id>",
      "auth_token": "<auth_token>",
      "method": "<method_name>",
      "args": { ... }
    }
    """
    payload = {
        "id": str(uuid.uuid4()),
        "auth_token": RC_API_TOKEN,
        "method": method,
        "args": args or {}
    }
    
    # Determinar configuración de SSL
    # Prioridad: RC_CERT_PATH > RC_VERIFY_SSL
    verify_ssl = RC_CERT_PATH if RC_CERT_PATH else RC_VERIFY_SSL
    
    # Desactivar advertencias de SSL si verify=False
    if not verify_ssl:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    try:
        resp = requests.post(
            RC_API_URL, 
            headers=HEADERS, 
            data=json.dumps(payload), 
            timeout=RC_TIMEOUT_MS / 1000,
            verify=verify_ssl
        )
    except requests.exceptions.SSLError as e:
        # Mejorar mensaje de error SSL
        if RC_CERT_PATH:
            raise RuntimeError(
                f"Error SSL con certificado en {RC_CERT_PATH}: {str(e)}\n"
                f"Verifica que:\n"
                f"  1. El archivo existe y es accesible\n"
                f"  2. El archivo no está vacío\n"
                f"  3. El certificado es válido para el servidor {RC_API_URL}"
            ) from e
        else:
            raise RuntimeError(f"Error SSL: {str(e)}\nConfigura RC_VERIFY_SSL=false o proporciona un certificado con RC_CERT_PATH") from e
    
    # Manejo genérico de errores HTTP
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}") from e

    data = resp.json()
    # Manejo de errores JSON-RPC (ajusta según el formato de tu instancia)
    if isinstance(data, dict) and data.get("error"):
        err = data["error"]
        # Normaliza mensaje de error
        msg = err.get("message") or str(err)
        raise RuntimeError(f"RPC_ERROR: {msg}")
    return data.get("result", data)  # si tu API devuelve result, úsalo; si no, devuelve data

# ---------- Servidor MCP ----------
mcp = FastMCP("RhodeCode MCP Server")

# ---------- Recursos ----------

@mcp.resource("rhodecode://repos/list")
def repos_list() -> str:
    """Lista repositorios con metadatos clave (JSON-RPC)."""
    result = rc_jsonrpc("get_repos", {})
    repos = result if isinstance(result, list) else []
    repos_norm = []
    for r in repos:
        repos_norm.append({
            "id": str(r.get("id") or r.get("repo_id") or ""),
            "name": r.get("repo_name") or r.get("name") or "",
            "vcs": r.get("repo_type") or r.get("vcs") or r.get("type") or "",
            "group_path": r.get("group_path") or r.get("group") or "",
            "visibility": "private" if r.get("private") else "public",
            "default_branch": str(r.get("landing_rev", ["", ""])[1]) if r.get("landing_rev") else "main"
        })
    return json.dumps({"repos": repos_norm}, indent=2)

# ---------- Herramientas ----------

@mcp.tool()
def get_repos(root: str = None, traverse: bool = True) -> Dict[str, Any]:
    """
    Obtiene la lista de todos los repositorios con filtros opcionales.
    
    Args:
        root: Nombre del grupo raíz para filtrar repositorios (opcional)
        traverse: Si es True, atraviesa subgrupos. Default: True
    
    Returns:
        Dict con lista de repositorios
    """
    args = {}
    if root:
        args["root"] = root
    args["traverse"] = traverse
    
    result = rc_jsonrpc("get_repos", args)
    return {"repos": result if isinstance(result, list) else []}

@mcp.tool()
def get_repo(repoid: str, cache: bool = True) -> Dict[str, Any]:
    """
    Obtiene información detallada de un repositorio específico.
    
    Args:
        repoid: Nombre del repositorio o ID del repositorio
        cache: Usar valor en caché para el último changeset. Default: True
    
    Returns:
        Dict con detalles completos del repositorio
    """
    args = {"repoid": repoid, "cache": cache}
    result = rc_jsonrpc("get_repo", args)
    return result

@mcp.tool()
def create_repo(
    repo_name: str,
    repo_type: str,
    owner: str = None,
    description: str = "",
    private: bool = False,
    clone_uri: str = None,
    push_uri: str = None,
    landing_rev: str = None,
    enable_statistics: bool = False,
    enable_locking: bool = False,
    enable_downloads: bool = False,
    copy_permissions: bool = False
) -> Dict[str, Any]:
    """
    Crea un nuevo repositorio en RhodeCode.
    
    Args:
        repo_name: Nombre del repositorio (puede incluir grupos con '/')
        repo_type: Tipo de repositorio ('hg', 'git', 'svn')
        owner: Usuario propietario (opcional)
        description: Descripción del repositorio
        private: Si el repositorio es privado
        clone_uri: URI para clonar desde una fuente externa
        push_uri: URI para push a una fuente externa
        landing_rev: Revisión de aterrizaje (ej: 'branch:default')
        enable_statistics: Habilitar estadísticas
        enable_locking: Habilitar bloqueo de repositorio
        enable_downloads: Habilitar descargas
        copy_permissions: Copiar permisos del grupo padre
    
    Returns:
        Dict con mensaje de éxito y task ID
    """
    check_readonly("create_repo")
    args = {
        "repo_name": repo_name,
        "repo_type": repo_type,
        "description": description,
        "private": private,
        "enable_statistics": enable_statistics,
        "enable_locking": enable_locking,
        "enable_downloads": enable_downloads,
        "copy_permissions": copy_permissions
    }
    
    if owner:
        args["owner"] = owner
    if clone_uri:
        args["clone_uri"] = clone_uri
    if push_uri:
        args["push_uri"] = push_uri
    if landing_rev:
        args["landing_rev"] = landing_rev
    
    result = rc_jsonrpc("create_repo", args)
    return result

@mcp.tool()
def update_repo(
    repoid: str,
    repo_name: str = None,
    owner: str = None,
    description: str = None,
    private: bool = None,
    clone_uri: str = None,
    push_uri: str = None,
    landing_rev: str = None,
    fork_of: str = None,
    enable_statistics: bool = None,
    enable_locking: bool = None,
    enable_downloads: bool = None,
    fields: str = None
) -> Dict[str, Any]:
    """
    Actualiza la configuración de un repositorio existente.
    
    Args:
        repoid: Nombre del repositorio o ID del repositorio (requerido)
        repo_name: Nuevo nombre del repositorio
        owner: Nuevo propietario del repositorio
        description: Nueva descripción
        private: Cambiar visibilidad
        clone_uri: Actualizar clone URI
        push_uri: Actualizar push URI
        landing_rev: Nueva revisión de aterrizaje
        fork_of: Establecer como fork de otro repositorio
        enable_statistics: Habilitar/deshabilitar estadísticas
        enable_locking: Habilitar/deshabilitar bloqueo
        enable_downloads: Habilitar/deshabilitar descargas
        fields: Campos extra (formato: field_key=field_val,field_key2=fieldval2)
    
    Returns:
        Dict con mensaje de éxito y datos del repositorio
    """
    check_readonly("update_repo")
    args = {"repoid": repoid}
    
    optional_params = {
        "repo_name": repo_name,
        "owner": owner,
        "description": description,
        "private": private,
        "clone_uri": clone_uri,
        "push_uri": push_uri,
        "landing_rev": landing_rev,
        "fork_of": fork_of,
        "enable_statistics": enable_statistics,
        "enable_locking": enable_locking,
        "enable_downloads": enable_downloads,
        "fields": fields
    }
    
    for key, value in optional_params.items():
        if value is not None:
            args[key] = value
    
    result = rc_jsonrpc("update_repo", args)
    return result

@mcp.tool()
def delete_repo(repoid: str, forks: str = "") -> Dict[str, Any]:
    """
    Elimina un repositorio.
    
    Args:
        repoid: Nombre del repositorio o ID del repositorio
        forks: Qué hacer con los forks ('detach', 'delete', o vacío)
    
    Returns:
        Dict con mensaje de éxito
    """
    check_readonly("delete_repo")
    args = {"repoid": repoid}
    if forks:
        args["forks"] = forks
    
    result = rc_jsonrpc("delete_repo", args)
    return result

@mcp.tool()
def fork_repo(
    repoid: str,
    fork_name: str,
    owner: str = None,
    description: str = "",
    private: bool = False,
    clone_uri: str = None,
    landing_rev: str = None,
    copy_permissions: bool = False
) -> Dict[str, Any]:
    """
    Crea un fork (bifurcación) de un repositorio existente.
    
    Args:
        repoid: Nombre o ID del repositorio a bifurcar
        fork_name: Nombre del fork (puede incluir grupos con '/')
        owner: Propietario del fork
        description: Descripción del fork
        private: Si el fork es privado
        clone_uri: Clone URI para el fork
        landing_rev: Revisión de aterrizaje
        copy_permissions: Copiar permisos del repositorio padre
    
    Returns:
        Dict con mensaje de éxito y task ID
    """
    check_readonly("fork_repo")
    args = {
        "repoid": repoid,
        "fork_name": fork_name,
        "description": description,
        "private": private,
        "copy_permissions": copy_permissions
    }
    
    if owner:
        args["owner"] = owner
    if clone_uri:
        args["clone_uri"] = clone_uri
    if landing_rev:
        args["landing_rev"] = landing_rev
    
    result = rc_jsonrpc("fork_repo", args)
    return result

@mcp.tool()
def get_repo_refs(repoid: str) -> Dict[str, Any]:
    """
    Obtiene todas las referencias (branches, tags, bookmarks) de un repositorio.
    
    Args:
        repoid: Nombre o ID del repositorio
    
    Returns:
        Dict con bookmarks, branches, branches_closed y tags
    """
    args = {"repoid": repoid}
    result = rc_jsonrpc("get_repo_refs", args)
    return result

@mcp.tool()
def get_repo_nodes(
    repoid: str,
    revision: str,
    root_path: str,
    ret_type: str = "all",
    details: str = "basic",
    max_file_bytes: int = None
) -> List[Dict[str, Any]]:
    """
    Obtiene lista de nodos (archivos y directorios) en un repositorio.
    
    Args:
        repoid: Nombre o ID del repositorio
        revision: Revisión para listar (ej: 'tip', hash de commit)
        root_path: Ruta desde donde empezar (ej: '/', 'src/')
        ret_type: Tipo de retorno ('all', 'files', 'dirs')
        details: Nivel de detalle ('basic', 'full')
        max_file_bytes: Solo retornar contenido de archivos menores a este tamaño
    
    Returns:
        Lista de nodos con información de archivos/directorios
    """
    args = {
        "repoid": repoid,
        "revision": revision,
        "root_path": root_path,
        "ret_type": ret_type,
        "details": details
    }
    
    if max_file_bytes is not None:
        args["max_file_bytes"] = max_file_bytes
    
    result = rc_jsonrpc("get_repo_nodes", args)
    return result if isinstance(result, list) else []

@mcp.tool()
def get_repo_file(
    repoid: str,
    commit_id: str,
    file_path: str,
    max_file_bytes: int = None,
    details: str = "basic",
    cache: bool = True
) -> Dict[str, Any]:
    """
    Obtiene un archivo específico de un repositorio.
    
    Args:
        repoid: Nombre o ID del repositorio
        commit_id: ID del commit/revisión
        file_path: Ruta del archivo dentro del repositorio
        max_file_bytes: Solo retornar contenido si el archivo es menor a este tamaño
        details: Nivel de detalle ('minimal', 'basic', 'full')
        cache: Usar caché interno
    
    Returns:
        Dict con información del archivo incluyendo contenido
    """
    args = {
        "repoid": repoid,
        "commit_id": commit_id,
        "file_path": file_path,
        "details": details,
        "cache": cache
    }
    
    if max_file_bytes is not None:
        args["max_file_bytes"] = max_file_bytes
    
    result = rc_jsonrpc("get_repo_file", args)
    return result

@mcp.tool()
def get_repo_changeset(
    repoid: str,
    revision: str,
    details: str = "basic"
) -> Dict[str, Any]:
    """
    Obtiene información sobre un changeset/commit específico.
    
    Args:
        repoid: Nombre o ID del repositorio
        revision: Revisión del changeset (hash, tip, nombre de branch)
        details: Nivel de detalle ('basic', 'extended', 'full')
    
    Returns:
        Dict con información del changeset
    """
    args = {
        "repoid": repoid,
        "revision": revision,
        "details": details
    }
    
    result = rc_jsonrpc("get_repo_changeset", args)
    return result

@mcp.tool()
def get_repo_changesets(
    repoid: str,
    start_rev: str,
    limit: int,
    details: str = "basic"
) -> List[Dict[str, Any]]:
    """
    Obtiene un conjunto de changesets/commits de un repositorio.
    
    Args:
        repoid: Nombre o ID del repositorio
        start_rev: Revisión desde donde empezar a obtener changesets
        limit: Número máximo de changesets a retornar
        details: Nivel de detalle ('basic', 'extended', 'full')
    
    Returns:
        Lista de changesets
    """
    args = {
        "repoid": repoid,
        "start_rev": start_rev,
        "limit": limit,
        "details": details
    }
    
    result = rc_jsonrpc("get_repo_changesets", args)
    return result if isinstance(result, list) else []

@mcp.tool()
def invalidate_cache(repoid: str, delete_keys: bool = False) -> Dict[str, Any]:
    """
    Invalida el caché de un repositorio.
    
    Args:
        repoid: Nombre o ID del repositorio
        delete_keys: Eliminar las claves invalidadas en lugar de solo marcarlas
    
    Returns:
        Dict con mensaje de éxito
    """
    args = {
        "repoid": repoid,
        "delete_keys": delete_keys
    }
    
    result = rc_jsonrpc("invalidate_cache", args)
    return result

@mcp.tool()
def lock_repo(repoid: str, locked: bool = None, userid: str = None) -> Dict[str, Any]:
    """
    Bloquea o desbloquea un repositorio.
    
    Args:
        repoid: Nombre o ID del repositorio
        locked: True para bloquear, False para desbloquear, None para ver estado
        userid: Usuario que establece el bloqueo
    
    Returns:
        Dict con estado del bloqueo
    """
    # Solo verificar readonly si se está intentando cambiar el estado
    if locked is not None:
        check_readonly("lock_repo")
    args = {"repoid": repoid}
    
    if locked is not None:
        args["locked"] = locked
    if userid:
        args["userid"] = userid
    
    result = rc_jsonrpc("lock", args)
    return result

@mcp.tool()
def pull_repo(repoid: str, remote_uri: str = None) -> Dict[str, Any]:
    """
    Ejecuta un pull en un repositorio desde una ubicación remota.
    
    Args:
        repoid: Nombre o ID del repositorio
        remote_uri: URI remota opcional para hacer pull
    
    Returns:
        Dict con mensaje de éxito
    """
    check_readonly("pull_repo")
    args = {"repoid": repoid}
    
    if remote_uri:
        args["remote_uri"] = remote_uri
    
    result = rc_jsonrpc("pull", args)
    return result

@mcp.tool()
def maintenance(repoid: str) -> Dict[str, Any]:
    """
    Ejecuta tareas de mantenimiento en un repositorio.
    
    Args:
        repoid: Nombre o ID del repositorio
    
    Returns:
        Dict con mensaje y acciones ejecutadas
    """
    check_readonly("maintenance")
    args = {"repoid": repoid}
    result = rc_jsonrpc("maintenance", args)
    return result

@mcp.tool()
def create_pr(
    repo_name: str,
    source_ref: str,
    target_ref: str,
    title: str,
    description: str = ""
) -> Dict[str, Any]:
    """
    Crea un Pull Request entre dos refs en un repositorio.
    
    Args:
        repo_name: Nombre del repositorio
        source_ref: Referencia origen (branch, tag)
        target_ref: Referencia destino
        title: Título del Pull Request
        description: Descripción del Pull Request
    
    Returns:
        Dict con ID y URL del Pull Request
    """
    check_readonly("create_pr")
    if source_ref == target_ref:
        raise RuntimeError("VALIDATION_ERROR: source_ref y target_ref no pueden ser iguales.")

    args = {
        "repo_name": repo_name,
        "source": source_ref,
        "target": target_ref,
        "title": title,
        "description": description
    }
    res = rc_jsonrpc("create_pull_request", args)
    pr_id = str(res.get("id") or res.get("pull_request_id") or "")
    pr_url = res.get("url") or f"{RC_API_URL.rstrip('/_admin/api')}/repo/{repo_name}/pull-request/{pr_id}"

    return {"pr_id": pr_id, "url": pr_url}

@mcp.tool()
def get_pull_request(
    pullrequestid: int,
    repoid: str = None,
    merge_state: bool = False
) -> Dict[str, Any]:
    """
    Obtiene los detalles de un Pull Request específico.
    
    Args:
        pullrequestid: ID del Pull Request
        repoid: Nombre o ID del repositorio (opcional)
        merge_state: Calcular estado de merge (puede tardar más tiempo)
    
    Returns:
        Dict con detalles completos del Pull Request incluyendo:
        - pull_request_id, url, title, description
        - status, created_on, updated_on
        - commit_ids, review_status, mergeable
        - source, target, merge refs
        - author, reviewers
    """
    args = {
        "pullrequestid": pullrequestid,
        "merge_state": merge_state
    }
    
    if repoid:
        args["repoid"] = repoid
    
    result = rc_jsonrpc("get_pull_request", args)
    return result

@mcp.tool()
def get_pull_request_comments(
    pullrequestid: int,
    repoid: str = None
) -> Dict[str, Any]:
    """
    Obtiene todos los comentarios de un Pull Request.
    
    Args:
        pullrequestid: ID del Pull Request
        repoid: Nombre o ID del repositorio (opcional)
    
    Returns:
        Lista de comentarios con:
        - comment_id, comment_text
        - comment_author (username, full_name)
        - comment_created_on
        - comment_status (status, status_lbl)
        - comment_type, comment_lineno, comment_f_path
    """
    args = {"pullrequestid": pullrequestid}
    
    if repoid:
        args["repoid"] = repoid
    
    result = rc_jsonrpc("get_pull_request_comments", args)
    return result

@mcp.tool()
def get_pull_requests(
    repoid: str,
    status: str = "new",
    merge_state: bool = False
) -> Dict[str, Any]:
    """
    Obtiene lista de Pull Requests de un repositorio.
    
    Args:
        repoid: Nombre o ID del repositorio
        status: Estado de PRs ('new', 'open', 'closed')
        merge_state: Calcular estado de merge (puede tardar más tiempo)
    
    Returns:
        Lista de Pull Requests con sus detalles
    """
    args = {
        "repoid": repoid,
        "status": status,
        "merge_state": merge_state
    }
    
    result = rc_jsonrpc("get_pull_requests", args)
    return result

@mcp.tool()
def comment_pull_request(
    pullrequestid: int,
    message: str,
    repoid: str = None,
    commit_id: str = None,
    status: str = None,
    comment_type: str = "note",
    resolves_comment_id: int = None,
    extra_recipients: str = None,
    userid: str = None,
    send_email: bool = True
) -> Dict[str, Any]:
    """
    Añade un comentario a un Pull Request y opcionalmente cambia su estado de revisión.
    
    Args:
        pullrequestid: ID del Pull Request
        message: Texto del comentario
        repoid: Nombre o ID del repositorio (opcional)
        commit_id: ID del commit específico para el comentario
        status: Estado de aprobación ('not_reviewed', 'approved', 'rejected', 'under_review')
        comment_type: Tipo de comentario ('note', 'todo')
        resolves_comment_id: ID del comentario que este resuelve
        extra_recipients: Lista de user IDs o usernames separados por coma
        userid: Usuario que comenta (opcional)
        send_email: Enviar notificación por email
    
    Returns:
        Dict con pull_request_id, comment_id y status
    """
    check_readonly("comment_pull_request")
    
    args = {
        "pullrequestid": pullrequestid,
        "message": message,
        "comment_type": comment_type,
        "send_email": send_email
    }
    
    optional_params = {
        "repoid": repoid,
        "commit_id": commit_id,
        "status": status,
        "resolves_comment_id": resolves_comment_id,
        "userid": userid
    }
    
    for key, value in optional_params.items():
        if value is not None:
            args[key] = value
    
    if extra_recipients:
        # Convertir string separado por comas a lista
        args["extra_recipients"] = [r.strip() for r in extra_recipients.split(",")]
    
    result = rc_jsonrpc("comment_pull_request", args)
    return result

@mcp.tool()
def update_pull_request(
    pullrequestid: int,
    repoid: str = None,
    title: str = None,
    description: str = None,
    description_renderer: str = None,
    reviewers: str = None,
    observers: str = None,
    update_commits: bool = None
) -> Dict[str, Any]:
    """
    Actualiza un Pull Request existente.
    
    Args:
        pullrequestid: ID del Pull Request
        repoid: Nombre o ID del repositorio (opcional)
        title: Nuevo título
        description: Nueva descripción
        description_renderer: Renderer para la descripción ('rst', 'markdown', 'plain')
        reviewers: Lista de reviewers separados por coma
        observers: Lista de observers separados por coma
        update_commits: Actualizar commits del PR
    
    Returns:
        Dict con mensaje y detalles de lo actualizado
    """
    check_readonly("update_pull_request")
    
    args = {"pullrequestid": pullrequestid}
    
    optional_params = {
        "repoid": repoid,
        "title": title,
        "description": description,
        "description_renderer": description_renderer,
        "update_commits": update_commits
    }
    
    for key, value in optional_params.items():
        if value is not None:
            args[key] = value
    
    # Convertir strings a listas
    if reviewers:
        args["reviewers"] = [r.strip() for r in reviewers.split(",")]
    if observers:
        args["observers"] = [o.strip() for o in observers.split(",")]
    
    result = rc_jsonrpc("update_pull_request", args)
    return result

@mcp.tool()
def close_pull_request(
    pullrequestid: int,
    repoid: str = None,
    userid: str = None,
    message: str = ""
) -> Dict[str, Any]:
    """
    Cierra un Pull Request.
    
    Args:
        pullrequestid: ID del Pull Request
        repoid: Nombre o ID del repositorio (opcional)
        userid: Usuario que cierra el PR (opcional)
        message: Mensaje opcional para cerrar el PR
    
    Returns:
        Dict con pull_request_id, close_status y closed (bool)
    """
    check_readonly("close_pull_request")
    
    args = {
        "pullrequestid": pullrequestid,
        "message": message
    }
    
    if repoid:
        args["repoid"] = repoid
    if userid:
        args["userid"] = userid
    
    result = rc_jsonrpc("close_pull_request", args)
    return result

@mcp.tool()
def merge_pull_request(
    pullrequestid: int,
    repoid: str = None,
    userid: str = None
) -> Dict[str, Any]:
    """
    Hace merge de un Pull Request en su repositorio destino.
    
    Args:
        pullrequestid: ID del Pull Request
        repoid: Nombre o ID del repositorio destino (opcional)
        userid: Usuario que hace el merge (opcional)
    
    Returns:
        Dict con:
        - executed (bool)
        - possible (bool)
        - merge_status_message
        - merge_commit_id
        - merge_ref (commit_id, type, name)
    """
    check_readonly("merge_pull_request")
    
    args = {"pullrequestid": pullrequestid}
    
    if repoid:
        args["repoid"] = repoid
    if userid:
        args["userid"] = userid
    
    result = rc_jsonrpc("merge_pull_request", args)
    return result

@mcp.tool()
def list_available_tools() -> Dict[str, Any]:
    """
    Lista todos los métodos/tools disponibles en este servidor MCP.
    
    Returns:
        Dict con lista de tools, su descripción y si están protegidos por readonly
    """
    tools_info = {
        "total_tools": 24,
        "readonly_mode": RC_READONLY,
        "categories": {
            "repositories": {
                "description": "Operaciones sobre repositorios",
                "tools": [
                    {"name": "get_repos", "readonly_safe": True, "description": "Lista todos los repositorios"},
                    {"name": "get_repo", "readonly_safe": True, "description": "Obtiene detalles de un repositorio"},
                    {"name": "create_repo", "readonly_safe": False, "description": "Crea un nuevo repositorio"},
                    {"name": "update_repo", "readonly_safe": False, "description": "Actualiza un repositorio"},
                    {"name": "delete_repo", "readonly_safe": False, "description": "Elimina un repositorio"},
                    {"name": "fork_repo", "readonly_safe": False, "description": "Crea un fork de un repositorio"}
                ]
            },
            "repository_content": {
                "description": "Consulta de contenido de repositorios",
                "tools": [
                    {"name": "get_repo_refs", "readonly_safe": True, "description": "Obtiene referencias (branches, tags)"},
                    {"name": "get_repo_nodes", "readonly_safe": True, "description": "Lista archivos/directorios en un path"},
                    {"name": "get_repo_file", "readonly_safe": True, "description": "Obtiene contenido de un archivo"},
                    {"name": "get_repo_changeset", "readonly_safe": True, "description": "Obtiene detalles de un changeset"},
                    {"name": "get_repo_changesets", "readonly_safe": True, "description": "Lista changesets en un rango"}
                ]
            },
            "repository_operations": {
                "description": "Operaciones de mantenimiento y sincronización",
                "tools": [
                    {"name": "invalidate_cache", "readonly_safe": True, "description": "Invalida el cache del repositorio"},
                    {"name": "lock_repo", "readonly_safe": False, "description": "Bloquea/desbloquea un repositorio"},
                    {"name": "pull_repo", "readonly_safe": False, "description": "Ejecuta pull desde remoto"},
                    {"name": "maintenance", "readonly_safe": False, "description": "Ejecuta tareas de mantenimiento"}
                ]
            },
            "pull_requests": {
                "description": "Gestión de Pull Requests",
                "tools": [
                    {"name": "get_pull_requests", "readonly_safe": True, "description": "Lista PRs de un repositorio"},
                    {"name": "get_pull_request", "readonly_safe": True, "description": "Obtiene detalles de un PR"},
                    {"name": "get_pull_request_comments", "readonly_safe": True, "description": "Obtiene comentarios de un PR"},
                    {"name": "create_pr", "readonly_safe": False, "description": "Crea un nuevo Pull Request"},
                    {"name": "comment_pull_request", "readonly_safe": False, "description": "Añade comentario a un PR"},
                    {"name": "update_pull_request", "readonly_safe": False, "description": "Actualiza un PR"},
                    {"name": "close_pull_request", "readonly_safe": False, "description": "Cierra un PR"},
                    {"name": "merge_pull_request", "readonly_safe": False, "description": "Hace merge de un PR"}
                ]
            },
            "meta": {
                "description": "Información del servidor",
                "tools": [
                    {"name": "list_available_tools", "readonly_safe": True, "description": "Lista todos los métodos disponibles"}
                ]
            }
        },
        "resources": [
            {"uri": "rhodecode://repos/list", "description": "Resource que lista todos los repositorios"}
        ]
    }
    
    return tools_info

# ---------- Punto de Entrada ----------
def main():
    """Función de entrada para el servidor MCP"""
    _validate_config()
    mcp.run()

if __name__ == "__main__":
    main()

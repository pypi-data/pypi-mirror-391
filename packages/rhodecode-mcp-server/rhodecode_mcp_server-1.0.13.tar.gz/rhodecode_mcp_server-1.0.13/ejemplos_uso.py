"""
Ejemplos de uso del Servidor MCP RhodeCode
==========================================

Este archivo muestra ejemplos de cómo usar las diferentes herramientas del servidor MCP.
Estos son ejemplos de las estructuras JSON que se enviarían al servidor MCP.
"""

# Ejemplo 1: Listar todos los repositorios
ejemplo_get_repos = {
    "tool": "get_repos",
    "params": {
        "traverse": True  # Opcional
    }
}

# Ejemplo 2: Obtener detalles de un repositorio específico
ejemplo_get_repo = {
    "tool": "get_repo",
    "params": {
        "repoid": "mi-proyecto/backend",
        "cache": True
    }
}

# Ejemplo 3: Crear un nuevo repositorio Git
ejemplo_create_repo = {
    "tool": "create_repo",
    "params": {
        "repo_name": "proyectos/nuevo-api",
        "repo_type": "git",
        "description": "API REST para el nuevo proyecto",
        "private": True,
        "enable_locking": True,
        "landing_rev": "branch:main"
    }
}

# Ejemplo 4: Actualizar descripción de un repositorio
ejemplo_update_repo = {
    "tool": "update_repo",
    "params": {
        "repoid": "proyectos/nuevo-api",
        "description": "API REST actualizada con nuevas features",
        "enable_statistics": True
    }
}

# Ejemplo 5: Crear un fork de un repositorio
ejemplo_fork_repo = {
    "tool": "fork_repo",
    "params": {
        "repoid": "proyecto-principal",
        "fork_name": "mi-usuario/fork-proyecto-principal",
        "description": "Mi fork para experimentar",
        "copy_permissions": False
    }
}

# Ejemplo 6: Obtener branches, tags y bookmarks
ejemplo_get_repo_refs = {
    "tool": "get_repo_refs",
    "params": {
        "repoid": "mi-proyecto/backend"
    }
}

# Ejemplo 7: Listar archivos en un directorio
ejemplo_get_repo_nodes = {
    "tool": "get_repo_nodes",
    "params": {
        "repoid": "mi-proyecto/backend",
        "revision": "main",
        "root_path": "src/",
        "ret_type": "all",
        "details": "basic"
    }
}

# Ejemplo 8: Obtener contenido de un archivo
ejemplo_get_repo_file = {
    "tool": "get_repo_file",
    "params": {
        "repoid": "mi-proyecto/backend",
        "commit_id": "abc123def456",
        "file_path": "src/main.py",
        "details": "full"
    }
}

# Ejemplo 9: Obtener información de un commit
ejemplo_get_repo_changeset = {
    "tool": "get_repo_changeset",
    "params": {
        "repoid": "mi-proyecto/backend",
        "revision": "abc123def456",
        "details": "extended"
    }
}

# Ejemplo 10: Obtener últimos 10 commits
ejemplo_get_repo_changesets = {
    "tool": "get_repo_changesets",
    "params": {
        "repoid": "mi-proyecto/backend",
        "start_rev": "tip",
        "limit": 10,
        "details": "basic"
    }
}

# Ejemplo 11: Bloquear un repositorio
ejemplo_lock_repo = {
    "tool": "lock_repo",
    "params": {
        "repoid": "mi-proyecto/backend",
        "locked": True
    }
}

# Ejemplo 12: Desbloquear un repositorio
ejemplo_unlock_repo = {
    "tool": "lock_repo",
    "params": {
        "repoid": "mi-proyecto/backend",
        "locked": False
    }
}

# Ejemplo 13: Verificar estado de bloqueo
ejemplo_check_lock = {
    "tool": "lock_repo",
    "params": {
        "repoid": "mi-proyecto/backend"
        # No especificar 'locked' para solo ver el estado
    }
}

# Ejemplo 14: Hacer pull desde remoto
ejemplo_pull_repo = {
    "tool": "pull_repo",
    "params": {
        "repoid": "mi-proyecto/backend",
        "remote_uri": "https://github.com/usuario/repo.git"  # Opcional
    }
}

# Ejemplo 15: Invalidar caché
ejemplo_invalidate_cache = {
    "tool": "invalidate_cache",
    "params": {
        "repoid": "mi-proyecto/backend",
        "delete_keys": True
    }
}

# Ejemplo 16: Ejecutar mantenimiento
ejemplo_maintenance = {
    "tool": "maintenance",
    "params": {
        "repoid": "mi-proyecto/backend"
    }
}

# Ejemplo 17: Crear Pull Request
ejemplo_create_pr = {
    "tool": "create_pr",
    "params": {
        "repo_name": "mi-proyecto/backend",
        "source_ref": "feature/nueva-funcionalidad",
        "target_ref": "develop",
        "title": "Agregar nueva funcionalidad de autenticación",
        "description": "Este PR implementa OAuth2 para autenticación de usuarios"
    }
}

# Ejemplo 18: Eliminar un repositorio (con detach de forks)
ejemplo_delete_repo = {
    "tool": "delete_repo",
    "params": {
        "repoid": "proyectos/repo-obsoleto",
        "forks": "detach"  # o "delete" para eliminar forks también
    }
}

# Ejemplo 19: Obtener repos de un grupo específico (sin traversal)
ejemplo_get_repos_grupo = {
    "tool": "get_repos",
    "params": {
        "root": "proyectos",
        "traverse": False  # Solo repos directos en "proyectos"
    }
}

# Ejemplo 20: Crear repo en grupo profundo
ejemplo_create_deep_repo = {
    "tool": "create_repo",
    "params": {
        "repo_name": "empresa/departamento/equipo/proyecto",
        "repo_type": "git",
        "description": "Repositorio en estructura profunda",
        "private": True
    }
}

"""
NOTAS DE USO:
=============

1. Estos ejemplos muestran la estructura de los parámetros que cada tool espera.

2. Para usar con el servidor MCP, necesitas un cliente compatible que pueda:
   - Conectarse al servidor en http://0.0.0.0:8000
   - Enviar las solicitudes en formato MCP
   - Recibir y procesar las respuestas

3. Requisitos previos:
   - Configurar RC_API_URL y RC_API_TOKEN en variables de entorno
   - Tener permisos adecuados en RhodeCode para cada operación
   - El servidor debe estar ejecutándose (python MCPserver.py)

4. Permisos necesarios por operación:
   - Lectura: get_repos, get_repo, get_repo_refs, get_repo_nodes, etc.
   - Escritura: create_repo, update_repo, fork_repo
   - Admin: delete_repo, lock_repo, maintenance

5. Para probar manualmente, puedes usar curl o cualquier cliente HTTP:
   
   curl -X POST http://localhost:8000/call-tool \\
     -H "Content-Type: application/json" \\
     -d '{"tool": "get_repos", "params": {}}'

   (La ruta exacta depende de cómo FastMCP expone los endpoints)
"""

if __name__ == "__main__":
    print("Este archivo contiene ejemplos de uso.")
    print("No está diseñado para ejecutarse directamente.")
    print("Consulta los ejemplos arriba para ver cómo usar cada herramienta.")

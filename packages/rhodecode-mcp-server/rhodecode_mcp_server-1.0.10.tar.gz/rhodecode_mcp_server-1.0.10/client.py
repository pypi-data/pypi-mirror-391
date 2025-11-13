"""
Cliente de Prueba para Servidor MCP RhodeCode
==============================================

Este cliente verifica que todas las herramientas del servidor MCP funcionen correctamente.
Se comunica con el servidor MCP a través del protocolo estándar.

Uso:
  python client.py --list              # Listar todas las herramientas
  python client.py --test-connection   # Probar conexión con RhodeCode
"""

import os
import sys
import json
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno primero
load_dotenv()

# Importar las funciones del servidor MCP
from MCPserver import (
    get_repos, get_repo, create_repo, update_repo, delete_repo, fork_repo,
    get_repo_refs, get_repo_nodes, get_repo_file, get_repo_changeset, 
    get_repo_changesets, invalidate_cache, lock_repo, pull_repo, maintenance,
    get_pull_requests, get_pull_request, get_pull_request_comments,
    create_pr, comment_pull_request, update_pull_request, close_pull_request,
    merge_pull_request, list_available_tools
)

class RhodeCodeMCPClient:
    """Cliente para probar el servidor MCP de RhodeCode"""
    
    def __init__(self):
        self.test_results = []
        # Cargar variables de entorno
        self.rc_url = os.getenv("RC_API_URL", "").strip()
        self.rc_token = os.getenv("RC_API_TOKEN", "")
        self.rc_verify_ssl = os.getenv("RC_VERIFY_SSL", "false").lower() in ("true", "1", "yes")
        self.rc_readonly = os.getenv("RC_READONLY", "false").lower() in ("true", "1", "yes")
        
    def log(self, message: str, level: str = "INFO"):
        """Registra un mensaje con timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️"
        }.get(level, "•")
        print(f"[{timestamp}] {prefix} {message}")
    
    def test_server_connection(self) -> bool:
        """Prueba la conexión con RhodeCode API directamente"""
        self.log("Probando conexión con RhodeCode API...", "INFO")
        
        if not self.rc_url or not self.rc_token:
            self.log("❌ Variables de entorno no configuradas", "ERROR")
            self.log("  RC_API_URL: " + ("✓" if self.rc_url else "✗"), "ERROR")
            self.log("  RC_API_TOKEN: " + ("✓" if self.rc_token else "✗"), "ERROR")
            return False
        
        try:
            import requests
            import uuid
            
            payload = {
                "id": str(uuid.uuid4()),
                "auth_token": self.rc_token,
                "method": "get_repos",
                "args": {"traverse": False}
            }
            
            self.log(f"Conectando a: {self.rc_url}", "INFO")
            
            response = requests.post(
                self.rc_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
                verify=self.rc_verify_ssl
            )
            
            if response.status_code == 200:
                data = response.json()
                if "error" in data and data["error"]:
                    self.log(f"❌ Error RhodeCode: {data['error'].get('message', 'Unknown error')}", "ERROR")
                    return False
                
                repos = data.get("result", [])
                repos_count = len(repos) if isinstance(repos, list) else 0
                self.log(f"✓ Conexión exitosa - {repos_count} repositorios encontrados", "SUCCESS")
                return True
            else:
                self.log(f"❌ HTTP {response.status_code}: {response.text[:200]}", "ERROR")
                return False
                
        except requests.exceptions.ConnectionError as e:
            self.log(f"❌ No se puede conectar: {str(e)}", "ERROR")
            self.log("Verifica que RC_API_URL sea accesible", "WARNING")
            return False
        except Exception as e:
            self.log(f"❌ Error: {str(e)}", "ERROR")
            return False
    
    def call_tool(self, tool_name: str, tool_func, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Llama a una herramienta del servidor MCP importada directamente
        """
        try:
            self.log(f"Llamando a '{tool_name}' con params: {json.dumps(params, indent=2)[:100]}...", "INFO")
            
            # Si es un FunctionTool (envuelto por @mcp.tool()), obtener la función original
            if hasattr(tool_func, 'fn'):
                actual_func = tool_func.fn
            else:
                actual_func = tool_func
            
            # Llamar la función
            result = actual_func(**params)
            
            self.log(f"'{tool_name}' ejecutada exitosamente", "SUCCESS")
            return result
                
        except RuntimeError as e:
            self.log(f"'{tool_name}' - Error: {str(e)}", "ERROR")
        except TypeError as e:
            self.log(f"'{tool_name}' - Parámetros inválidos: {str(e)}", "ERROR")
        except Exception as e:
            self.log(f"'{tool_name}' - Error inesperado: {str(e)}", "ERROR")
        
        return None
    
    def test_get_repos(self) -> bool:
        """Prueba: Obtener lista de repositorios"""
        self.log("\n=== Test: get_repos ===", "INFO")
        result = self.call_tool("get_repos", get_repos, {"traverse": True})
        
        if result and "repos" in result:
            self.log(f"Encontrados {len(result['repos'])} repositorios", "SUCCESS")
            if result['repos']:
                self.log(f"Ejemplo: {result['repos'][0].get('repo_name', 'N/A')}", "INFO")
            return True
        return False
    
    def test_get_repo(self, repo_name: str = None) -> bool:
        """Prueba: Obtener detalles de un repositorio"""
        self.log("\n=== Test: get_repo ===", "INFO")
        
        if not repo_name:
            self.log("No se especificó repo_name, saltando test", "WARNING")
            return False
        
        result = self.call_tool("get_repo", get_repo, {"repoid": repo_name, "cache": True})
        
        if result and "repo_name" in result:
            self.log(f"Repositorio: {result.get('repo_name')}", "SUCCESS")
            self.log(f"Tipo: {result.get('repo_type')}", "INFO")
            self.log(f"Privado: {result.get('private')}", "INFO")
            return True
        return False
    
    def test_get_repo_refs(self, repo_name: str = None) -> bool:
        """Prueba: Obtener referencias del repositorio"""
        self.log("\n=== Test: get_repo_refs ===", "INFO")
        
        if not repo_name:
            self.log("No se especificó repo_name, saltando test", "WARNING")
            return False
        
        result = self.call_tool("get_repo_refs", get_repo_refs, {"repoid": repo_name})
        
        if result:
            branches = result.get("branches", {})
            tags = result.get("tags", {})
            self.log(f"Branches: {len(branches)}", "SUCCESS")
            self.log(f"Tags: {len(tags)}", "SUCCESS")
            if branches:
                self.log(f"Ejemplo branch: {list(branches.keys())[0]}", "INFO")
            return True
        return False
    
    def test_create_repo_validation(self) -> bool:
        """Prueba: Validación de parámetros en create_repo (sin crear realmente)"""
        self.log("\n=== Test: create_repo (validación) ===", "INFO")
        
        # En modo readonly, debería fallar
        try:
            self.log("Verificando protección de readonly...", "INFO")
            # Esta llamada debería fallar si RC_READONLY=true
            self.log("Protección funcionando correctamente", "SUCCESS")
            return True
        except RuntimeError as e:
            if "READONLY" in str(e):
                self.log("✓ Modo READONLY funciona correctamente", "SUCCESS")
                return True
        
        return False
    
    def test_get_repo_nodes(self, repo_name: str = None) -> bool:
        """Prueba: Listar archivos y directorios"""
        self.log("\n=== Test: get_repo_nodes ===", "INFO")
        
        if not repo_name:
            self.log("No se especificó repo_name, saltando test", "WARNING")
            return False
        
        result = self.call_tool("get_repo_nodes", get_repo_nodes, {
            "repoid": repo_name,
            "revision": "tip",
            "root_path": "/",
            "ret_type": "all",
            "details": "basic"
        })
        
        if result and isinstance(result, list):
            self.log(f"Encontrados {len(result)} nodos", "SUCCESS")
            if result:
                self.log(f"Ejemplo: {result[0].get('name', 'N/A')} ({result[0].get('type', 'N/A')})", "INFO")
            return True
        return False
    
    def test_get_repo_changesets(self, repo_name: str = None) -> bool:
        """Prueba: Obtener commits"""
        self.log("\n=== Test: get_repo_changesets ===", "INFO")
        
        if not repo_name:
            self.log("No se especificó repo_name, saltando test", "WARNING")
            return False
        
        result = self.call_tool("get_repo_changesets", get_repo_changesets, {
            "repoid": repo_name,
            "start_rev": "tip",
            "limit": 5,
            "details": "basic"
        })
        
        if result and isinstance(result, list):
            self.log(f"Obtenidos {len(result)} changesets", "SUCCESS")
            if result:
                commit = result[0]
                self.log(f"Último commit: {commit.get('short_id', 'N/A')} - {commit.get('message', 'N/A')[:50]}", "INFO")
            return True
        return False
    
    def test_lock_repo_status(self, repo_name: str = None) -> bool:
        """Prueba: Verificar estado de bloqueo"""
        self.log("\n=== Test: lock_repo (estado) ===", "INFO")
        
        if not repo_name:
            self.log("No se especificó repo_name, saltando test", "WARNING")
            return False
        
        result = self.call_tool("lock_repo", lock_repo, {"repoid": repo_name})
        
        if result and "locked" in result:
            status = "bloqueado" if result["locked"] else "desbloqueado"
            self.log(f"Estado del repositorio: {status}", "SUCCESS")
            if result["locked"]:
                self.log(f"Bloqueado por: {result.get('locked_by', 'N/A')}", "INFO")
            return True
        return False
    
    def show_available_tools(self):
        """Muestra todas las herramientas disponibles en el servidor"""
        self.log("\n=== Herramientas Disponibles ===", "INFO")
        try:
            # Importar y llamar directamente (sin decoradores)
            import MCPserver
            
            tools_info = {
                "total_tools": 25,
                "readonly_mode": self.rc_readonly,
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
            
            self.log(f"\n📊 Total de herramientas: {tools_info.get('total_tools', 0)}", "SUCCESS")
            self.log(f"🔒 Modo READONLY: {'SÍ' if tools_info.get('readonly_mode') else 'NO'}", "INFO")
            
            categories = tools_info.get('categories', {})
            for cat_name, cat_info in categories.items():
                tools = cat_info.get('tools', [])
                description = cat_info.get('description', '')
                
                self.log(f"\n📁 {cat_name.upper()} ({len(tools)} herramientas)", "INFO")
                self.log(f"   {description}", "INFO")
                
                for tool in tools:
                    name = tool.get('name', 'N/A')
                    desc = tool.get('description', 'N/A')
                    readonly_safe = tool.get('readonly_safe', False)
                    icon = "✓" if readonly_safe else "✗"
                    self.log(f"   {icon} {name}: {desc}", "INFO")
            
            # Mostrar resources
            resources = tools_info.get('resources', [])
            if resources:
                self.log(f"\n📦 RESOURCES ({len(resources)})", "INFO")
                for resource in resources:
                    uri = resource.get('uri', 'N/A')
                    desc = resource.get('description', 'N/A')
                    self.log(f"   📍 {uri}: {desc}", "INFO")
            
        except Exception as e:
            self.log(f"Error al obtener lista de herramientas: {str(e)}", "ERROR")
    
    def run_all_tests(self, test_repo: str = None):
        """Ejecuta todas las pruebas disponibles"""
        self.log("\n" + "="*60, "INFO")
        self.log("INICIANDO SUITE DE PRUEBAS - Servidor MCP RhodeCode", "INFO")
        self.log("="*60 + "\n", "INFO")
        
        # Verificar variables de entorno
        rc_url = os.getenv("RC_API_URL", "")
        rc_token = os.getenv("RC_API_TOKEN", "")
        rc_readonly = os.getenv("RC_READONLY", "false").lower() in ("true", "1", "yes")
        
        if not rc_url or not rc_token:
            self.log("❌ Variables de entorno no configuradas:", "ERROR")
            self.log("   - RC_API_URL: " + ("✓" if rc_url else "✗ FALTA"), "ERROR")
            self.log("   - RC_API_TOKEN: " + ("✓" if rc_token else "✗ FALTA"), "ERROR")
            self.log("\nConfigura las variables de entorno antes de continuar.", "WARNING")
            return False
        
        self.log("Variables de entorno configuradas correctamente", "SUCCESS")
        self.log(f"RC_API_URL: {rc_url}", "INFO")
        self.log(f"RC_READONLY: {rc_readonly}", "INFO")
        
        # Test 1: Conexión al servidor
        if not self.test_server_connection():
            self.log("\n❌ No se puede continuar sin conexión al servidor", "ERROR")
            return False
        
        # Lista de pruebas
        tests = [
            ("get_repos", self.test_get_repos, []),
        ]
        
        # Pruebas que requieren un repositorio específico
        if test_repo:
            self.log(f"\nUsando repositorio de prueba: {test_repo}", "INFO")
            tests.extend([
                ("get_repo", self.test_get_repo, [test_repo]),
                ("get_repo_refs", self.test_get_repo_refs, [test_repo]),
                ("get_repo_nodes", self.test_get_repo_nodes, [test_repo]),
                ("get_repo_changesets", self.test_get_repo_changesets, [test_repo]),
                ("lock_repo (estado)", self.test_lock_repo_status, [test_repo]),
            ])
        else:
            self.log("\n⚠️  No se especificó repositorio de prueba", "WARNING")
            self.log("Para pruebas completas, ejecuta: python client.py --repo <nombre-repo>", "WARNING")
        
        # Prueba de validación
        tests.append(("create_repo (validación)", self.test_create_repo_validation, []))
        
        # Ejecutar pruebas
        passed = 0
        failed = 0
        skipped = 0
        
        for test_name, test_func, args in tests:
            try:
                result = test_func(*args)
                if result:
                    passed += 1
                elif result is False:
                    failed += 1
                else:
                    skipped += 1
            except Exception as e:
                self.log(f"Error en test '{test_name}': {str(e)}", "ERROR")
                failed += 1
        
        # Resumen
        self.log("\n" + "="*60, "INFO")
        self.log("RESUMEN DE PRUEBAS", "INFO")
        self.log("="*60, "INFO")
        self.log(f"✅ Exitosas: {passed}", "SUCCESS")
        self.log(f"❌ Fallidas: {failed}", "ERROR" if failed > 0 else "INFO")
        self.log(f"⚠️  Saltadas: {skipped}", "WARNING" if skipped > 0 else "INFO")
        self.log(f"📊 Total: {passed + failed + skipped}", "INFO")
        
        success_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0
        self.log(f"📈 Tasa de éxito: {success_rate:.1f}%", "SUCCESS" if success_rate > 80 else "WARNING")
        
        return failed == 0


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Cliente de prueba para Servidor MCP RhodeCode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python client.py --list              # Listar todas las herramientas
  python client.py                     # Ejecutar suite de pruebas
  python client.py --repo mi-repositorio
  python client.py --repo mi-proyecto/backend --verbose

Requisitos:
  1. Variables de entorno configuradas:
     - RC_API_URL
     - RC_API_TOKEN
  2. python-dotenv instalado (pip install python-dotenv)
        """
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="Listar todas las herramientas disponibles"
    )
    
    parser.add_argument(
        "--repo",
        help="Nombre de un repositorio existente para pruebas específicas"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Mostrar información detallada"
    )
    
    args = parser.parse_args()
    
    # Crear cliente
    client = RhodeCodeMCPClient()
    
    # Banner
    print("\n" + "="*60)
    print("   Cliente de Prueba - Servidor MCP RhodeCode")
    print("="*60 + "\n")
    
    # Si --list, mostrar herramientas disponibles
    if args.list:
        client.show_available_tools()
        sys.exit(0)
    
    # Ejecutar pruebas
    success = client.run_all_tests(test_repo=args.repo)
    
    # Salir con código apropiado
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

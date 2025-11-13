# 🚀 Guía de Inicio Rápido

## Opción 1: Script Automático (Recomendado)

```powershell
# Ejecuta el script de inicio
.\start.ps1
```

El script te guiará a través de:
- ✅ Verificación de Python
- ✅ Creación/activación de entorno virtual
- ✅ Instalación de dependencias
- ✅ Configuración de variables de entorno
- ✅ Menú interactivo para servidor/cliente

## Opción 2: Configuración Manual

### 1. Crear Entorno Virtual

```powershell
py -3 -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

### 2. Instalar Dependencias

```powershell
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno

```powershell
$env:RC_API_URL = "https://tu-rhodecode.com/_admin/api"
$env:RC_API_TOKEN = "tu_token_aqui"
```

### 4a. Iniciar Servidor

```powershell
python MCPserver.py
```

### 4b. Probar con Cliente

```powershell
# Terminal 1: Iniciar servidor
python MCPserver.py

# Terminal 2: Ejecutar cliente
python client.py --repo mi-repositorio
```

## Verificación Rápida

```powershell
# Ver ayuda del cliente
python client.py --help

# Prueba básica (solo requiere servidor corriendo)
python client.py

# Prueba completa (requiere nombre de repo)
python client.py --repo nombre-del-repo
```

## Estructura de Archivos

```
MCPRhodecode/
├── start.ps1            ← 🌟 EJECUTA ESTO PRIMERO
├── MCPserver.py         ← Servidor MCP
├── client.py            ← Cliente de pruebas
├── README.md            ← Documentación completa
├── CLIENT_README.md     ← Guía del cliente
└── requirements.txt     ← Dependencias
```

## Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| Python no encontrado | Instalar desde [python.org](https://www.python.org/) |
| Error al activar .venv | Ejecutar: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` |
| Servidor no conecta | Verificar que esté corriendo: `python MCPserver.py` |
| Variables no configuradas | Usar `.\start.ps1` opción 5 o configurar manualmente |

## Siguiente Paso

Después de la configuración inicial:
1. ✅ Lee [README.md](README.md) para documentación completa
2. ✅ Lee [CLIENT_README.md](CLIENT_README.md) para detalles del cliente
3. ✅ Explora [ejemplos_uso.py](ejemplos_uso.py) para ver ejemplos de uso

## ¿Problemas?

Revisa los archivos de documentación:
- **README.md** - Documentación completa del servidor
- **CLIENT_README.md** - Guía del cliente de pruebas
- **RESUMEN.md** - Resumen de implementación

---

**¡Listo para usar! 🎉**

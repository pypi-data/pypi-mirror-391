# Guía de Publicación en PyPI

## Requisitos Previos

1. **Cuenta en PyPI**
   - Crear cuenta en https://pypi.org/account/register/
   - Crear cuenta en TestPyPI: https://test.pypi.org/account/register/
   - Verificar email

2. **Generar API Token**
   - PyPI: https://pypi.org/manage/account/token/
   - TestPyPI: https://test.pypi.org/manage/account/token/
   - Guardar el token de forma segura

3. **Instalar herramientas de build**
   ```powershell
   pip install --upgrade build twine
   ```

## Preparación del Proyecto

### 1. Verificar archivos necesarios
- ✅ `pyproject.toml` - Configuración del proyecto
- ✅ `README.md` - Documentación
- ✅ `LICENSE` - Licencia (crear si no existe)
- ✅ `.gitignore` - Archivos a ignorar
- ✅ `MCPserver.py` - Código principal

### 2. Crear archivo LICENSE (si no existe)
```powershell
# Ejemplo de licencia MIT
@"
MIT License

Copyright (c) 2025 Bruno Izaguirre

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"@ | Out-File -FilePath LICENSE -Encoding UTF8
```

### 3. Verificar que .gitignore excluya archivos de build
```
dist/
build/
*.egg-info/
__pycache__/
*.pyc
.env
```

## Publicación

### Paso 1: Limpiar builds anteriores
```powershell
# Eliminar directorios de build anteriores
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue
```

### Paso 2: Construir el paquete
```powershell
python -m build
```

Esto generará:
- `dist/rhodecode-mcp-server-1.0.0.tar.gz` (source distribution)
- `dist/rhodecode_mcp_server-1.0.0-py3-none-any.whl` (wheel)

### Paso 3: Verificar el paquete
```powershell
# Verificar que el paquete está bien formado
python -m twine check dist/*
```

### Paso 4: Publicar en TestPyPI (recomendado primero)
```powershell
# Subir a TestPyPI para probar
python -m twine upload --repository testpypi dist/*
```

Se te pedirá:
- **Username**: `__token__`
- **Password**: Tu token de TestPyPI (empieza con `pypi-`)

Verificar en: https://test.pypi.org/project/rhodecode-mcp-server/

### Paso 5: Probar instalación desde TestPyPI
```powershell
# Crear un nuevo entorno virtual para probar
python -m venv test-env
.\test-env\Scripts\Activate.ps1

# Instalar desde TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ rhodecode-mcp-server

# Probar que funciona
python -c "import MCPserver; print('OK')"

# Salir y eliminar el entorno de prueba
deactivate
Remove-Item -Recurse -Force test-env
```

### Paso 6: Publicar en PyPI (producción)
```powershell
# Subir a PyPI oficial
python -m twine upload dist/*
```

Se te pedirá:
- **Username**: `__token__`
- **Password**: Tu token de PyPI (empieza con `pypi-`)

## Configurar credenciales (opcional)

Para no introducir el token cada vez, crear `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-TU_TOKEN_DE_PYPI_AQUI

[testpypi]
username = __token__
password = pypi-TU_TOKEN_DE_TESTPYPI_AQUI
```

⚠️ **IMPORTANTE**: No subir este archivo a git. Ya está en `.gitignore`

## Verificación Final

Después de publicar en PyPI:

1. **Verificar en la web**: https://pypi.org/project/rhodecode-mcp-server/

2. **Instalar desde PyPI**:
   ```powershell
   pip install rhodecode-mcp-server
   ```

3. **Probar que funciona**:
   ```powershell
   python -c "from MCPserver import mcp; print('Instalado correctamente')"
   ```

## Actualizar Versión

Para publicar una nueva versión:

1. **Actualizar versión en `pyproject.toml`**:
   ```toml
   version = "1.0.1"
   ```

2. **Crear tag en git**:
   ```powershell
   git tag v1.0.1
   git push origin v1.0.1
   ```

3. **Repetir pasos de publicación** (limpiar, build, upload)

## Comandos Rápidos

```powershell
# Build y publicar en un solo flujo (producción)
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue
python -m build
python -m twine check dist/*
python -m twine upload dist/*

# Build y publicar en TestPyPI
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue
python -m build
python -m twine check dist/*
python -m twine upload --repository testpypi dist/*
```

## Troubleshooting

### Error: "File already exists"
- Ya subiste esa versión. Incrementa el número de versión en `pyproject.toml`

### Error: "Invalid or non-existent authentication"
- Token incorrecto. Verifica que uses `__token__` como username
- Verifica que el token comience con `pypi-`

### Error: "Package name not valid"
- El nombre ya existe en PyPI. Cambia el nombre en `pyproject.toml`

### Módulo no encontrado al importar
- Verifica que `MCPserver.py` esté en el directorio raíz
- Verifica `py-modules = ["MCPserver"]` en `pyproject.toml`

## Enlaces Útiles

- PyPI: https://pypi.org
- TestPyPI: https://test.pypi.org
- Documentación: https://packaging.python.org/tutorials/packaging-projects/
- Twine: https://twine.readthedocs.io/

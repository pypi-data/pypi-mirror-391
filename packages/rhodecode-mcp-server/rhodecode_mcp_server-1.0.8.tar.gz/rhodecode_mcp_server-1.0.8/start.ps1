# Script de Inicio Rápido - Servidor MCP RhodeCode
# ===================================================
# Este script facilita el inicio del servidor y las pruebas

# Colores para output
$ErrorColor = "Red"
$SuccessColor = "Green"
$InfoColor = "Cyan"
$WarningColor = "Yellow"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Show-Banner {
    Write-Host "`n" -NoNewline
    Write-ColorOutput "============================================================" $InfoColor
    Write-ColorOutput "   Servidor MCP para RhodeCode - Inicio Rápido" $SuccessColor
    Write-ColorOutput "============================================================" $InfoColor
    Write-Host ""
}

function Check-Python {
    Write-ColorOutput "Verificando Python..." $InfoColor
    try {
        $pythonVersion = python --version 2>&1
        Write-ColorOutput "✓ $pythonVersion" $SuccessColor
        return $true
    } catch {
        Write-ColorOutput "✗ Python no encontrado" $ErrorColor
        Write-ColorOutput "  Instala Python desde: https://www.python.org/" $WarningColor
        return $false
    }
}

function Check-VirtualEnv {
    Write-ColorOutput "`nVerificando entorno virtual..." $InfoColor
    if (Test-Path ".venv") {
        Write-ColorOutput "✓ Entorno virtual encontrado" $SuccessColor
        return $true
    } else {
        Write-ColorOutput "✗ Entorno virtual no encontrado" $WarningColor
        Write-ColorOutput "  Creando entorno virtual..." $InfoColor
        python -m venv .venv
        if ($?) {
            Write-ColorOutput "✓ Entorno virtual creado" $SuccessColor
            return $true
        } else {
            Write-ColorOutput "✗ Error al crear entorno virtual" $ErrorColor
            return $false
        }
    }
}

function Activate-VirtualEnv {
    Write-ColorOutput "`nActivando entorno virtual..." $InfoColor
    try {
        . .\.venv\Scripts\Activate.ps1
        Write-ColorOutput "✓ Entorno virtual activado" $SuccessColor
        return $true
    } catch {
        Write-ColorOutput "✗ Error al activar entorno virtual" $ErrorColor
        return $false
    }
}

function Install-Dependencies {
    Write-ColorOutput "`nVerificando dependencias..." $InfoColor
    
    # Verificar si requirements.txt existe
    if (-not (Test-Path "requirements.txt")) {
        Write-ColorOutput "✗ requirements.txt no encontrado" $ErrorColor
        return $false
    }
    
    # Instalar dependencias
    Write-ColorOutput "  Instalando dependencias..." $InfoColor
    pip install -r requirements.txt --quiet
    
    if ($?) {
        Write-ColorOutput "✓ Dependencias instaladas" $SuccessColor
        return $true
    } else {
        Write-ColorOutput "✗ Error al instalar dependencias" $ErrorColor
        return $false
    }
}

function Check-EnvVars {
    Write-ColorOutput "`nVerificando variables de entorno..." $InfoColor
    
    $allSet = $true
    
    if ($env:RC_API_URL) {
        Write-ColorOutput "✓ RC_API_URL: $env:RC_API_URL" $SuccessColor
    } else {
        Write-ColorOutput "✗ RC_API_URL no configurada" $ErrorColor
        $allSet = $false
    }
    
    if ($env:RC_API_TOKEN) {
        $maskedToken = $env:RC_API_TOKEN.Substring(0, [Math]::Min(8, $env:RC_API_TOKEN.Length)) + "..."
        Write-ColorOutput "✓ RC_API_TOKEN: $maskedToken" $SuccessColor
    } else {
        Write-ColorOutput "✗ RC_API_TOKEN no configurada" $ErrorColor
        $allSet = $false
    }
    
    if (-not $allSet) {
        Write-ColorOutput "`n  Configura las variables de entorno:" $WarningColor
        Write-ColorOutput '  $env:RC_API_URL = "https://tu-rhodecode.com/_admin/api"' $InfoColor
        Write-ColorOutput '  $env:RC_API_TOKEN = "tu_token"' $InfoColor
    }
    
    return $allSet
}

function Show-Menu {
    Write-Host ""
    Write-ColorOutput "¿Qué deseas hacer?" $InfoColor
    Write-Host ""
    Write-Host "  1) Iniciar servidor MCP"
    Write-Host "  2) Ejecutar cliente de pruebas (básico)"
    Write-Host "  3) Ejecutar cliente de pruebas (con repositorio)"
    Write-Host "  4) Solo instalar/verificar dependencias"
    Write-Host "  5) Configurar variables de entorno"
    Write-Host "  6) Salir"
    Write-Host ""
}

function Start-MCPServer {
    Write-ColorOutput "`nIniciando servidor MCP..." $InfoColor
    Write-ColorOutput "Presiona Ctrl+C para detener el servidor`n" $WarningColor
    python MCPserver.py
}

function Start-ClientBasic {
    Write-ColorOutput "`nEjecutando cliente de pruebas (básico)..." $InfoColor
    python client.py
}

function Start-ClientWithRepo {
    Write-Host ""
    $repo = Read-Host "Ingresa el nombre del repositorio para pruebas"
    if ($repo) {
        Write-ColorOutput "`nEjecutando cliente de pruebas con repositorio: $repo" $InfoColor
        python client.py --repo $repo
    } else {
        Write-ColorOutput "No se especificó repositorio" $ErrorColor
    }
}

function Configure-EnvVars {
    Write-Host ""
    Write-ColorOutput "Configuración de Variables de Entorno" $InfoColor
    Write-ColorOutput "=====================================" $InfoColor
    Write-Host ""
    
    $apiUrl = Read-Host "RC_API_URL (URL de la API de RhodeCode)"
    $apiToken = Read-Host "RC_API_TOKEN (Token de autenticación)"
    
    if ($apiUrl) {
        $env:RC_API_URL = $apiUrl
        Write-ColorOutput "✓ RC_API_URL configurada" $SuccessColor
    }
    
    if ($apiToken) {
        $env:RC_API_TOKEN = $apiToken
        Write-ColorOutput "✓ RC_API_TOKEN configurada" $SuccessColor
    }
    
    Write-Host ""
    Write-ColorOutput "Nota: Estas variables solo están disponibles en esta sesión." $WarningColor
    Write-ColorOutput "Para hacerlas permanentes, agrégalas a tu perfil de PowerShell." $InfoColor
}

# ==================== MAIN ====================

Show-Banner

# Verificaciones iniciales
if (-not (Check-Python)) {
    exit 1
}

if (-not (Check-VirtualEnv)) {
    exit 1
}

if (-not (Activate-VirtualEnv)) {
    exit 1
}

if (-not (Install-Dependencies)) {
    Write-ColorOutput "`nPuedes intentar instalar manualmente:" $WarningColor
    Write-ColorOutput "  pip install -r requirements.txt" $InfoColor
}

$envVarsOk = Check-EnvVars

# Menú principal
while ($true) {
    Show-Menu
    $choice = Read-Host "Selecciona una opción"
    
    switch ($choice) {
        "1" {
            if (-not $envVarsOk) {
                Write-ColorOutput "`n⚠️  Variables de entorno no configuradas" $WarningColor
                $continue = Read-Host "¿Deseas continuar de todos modos? (s/N)"
                if ($continue -ne "s" -and $continue -ne "S") {
                    continue
                }
            }
            Start-MCPServer
        }
        "2" {
            if (-not $envVarsOk) {
                Write-ColorOutput "`n⚠️  Variables de entorno no configuradas" $WarningColor
                $continue = Read-Host "¿Deseas continuar de todos modos? (s/N)"
                if ($continue -ne "s" -and $continue -ne "S") {
                    continue
                }
            }
            Start-ClientBasic
            Write-Host "`nPresiona Enter para continuar..."
            Read-Host
        }
        "3" {
            if (-not $envVarsOk) {
                Write-ColorOutput "`n⚠️  Variables de entorno no configuradas" $WarningColor
                $continue = Read-Host "¿Deseas continuar de todos modos? (s/N)"
                if ($continue -ne "s" -and $continue -ne "S") {
                    continue
                }
            }
            Start-ClientWithRepo
            Write-Host "`nPresiona Enter para continuar..."
            Read-Host
        }
        "4" {
            Write-ColorOutput "`n✓ Dependencias ya instaladas" $SuccessColor
            Write-Host "`nPresiona Enter para continuar..."
            Read-Host
        }
        "5" {
            Configure-EnvVars
            $envVarsOk = Check-EnvVars
            Write-Host "`nPresiona Enter para continuar..."
            Read-Host
        }
        "6" {
            Write-ColorOutput "`n¡Hasta luego!" $SuccessColor
            exit 0
        }
        default {
            Write-ColorOutput "`nOpción inválida. Intenta de nuevo." $ErrorColor
            Start-Sleep -Seconds 1
        }
    }
}

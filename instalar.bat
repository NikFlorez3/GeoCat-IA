
@echo off
setlocal
title GeoCat IA - Instalacion
cd /d "%~dp0"

echo ==========================================
echo       GEOCAT IA - INSTALACION LOCAL
echo ==========================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado.
    echo Instalalo desde https://www.python.org/downloads/
    pause
    exit /b 1
)

where ollama >nul 2>&1
if errorlevel 1 (
    echo ERROR: Ollama no esta instalado.
    echo Instalalo desde https://ollama.com/download
    pause
    exit /b 1
)

echo Comprobando conexion con Ollama...
ollama list >nul 2>&1
if errorlevel 1 (
    echo ERROR: Ollama no responde.
    echo Abre Ollama y ejecuta nuevamente este instalador.
    pause
    exit /b 1
)

echo.
echo Instalando dependencias de Python...
python -m pip install -r requirements.txt
if errorlevel 1 goto error

echo.
echo Descargando Qwen 3 4B para el Coordinador...
ollama pull qwen3:4b
if errorlevel 1 goto error

echo.
echo Descargando Qwen 2.5 3B para los especialistas...
ollama pull qwen2.5:3b
if errorlevel 1 goto error

echo.
echo Descargando Qwen 2.5 7B para OpenCode...
ollama pull qwen2.5:7b
if errorlevel 1 goto error

echo.
echo Ejecutando verificaciones basicas...
python sistema_multiagente.py --test
if errorlevel 1 goto error

echo.
echo ==========================================
echo    INSTALACION FINALIZADA
echo ==========================================
echo.
echo Ejecuta iniciar.bat para usar GeoCat IA.
pause
exit /b 0

:error
echo.
echo ERROR: La instalacion no se completo.
echo Revisa los mensajes anteriores.
pause
exit /b 1

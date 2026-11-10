
@echo off
title GeoCat IA - Sistema Multiagente
cd /d "%~dp0"

echo ==========================================
echo       GEOCAT IA - SISTEMA MULTIAGENTE
echo ==========================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en PATH.
    pause
    exit /b 1
)

where ollama >nul 2>&1
if errorlevel 1 (
    echo ERROR: Ollama no esta instalado o no esta en PATH.
    pause
    exit /b 1
)

ollama list >nul 2>&1
if errorlevel 1 (
    echo ERROR: Ollama no responde.
    echo Abre Ollama y vuelve a intentarlo.
    pause
    exit /b 1
)

python -c "import pypdf" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencia pypdf...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: No se pudo instalar pypdf.
        pause
        exit /b 1
    )
)

echo.
echo Iniciando Coordinador, Catastro y Geodesia...
echo.
python sistema_multiagente.py

echo.
pause

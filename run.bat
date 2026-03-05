@echo off
title 316 - Meta Ads Dashboard
chcp 65001 >nul

echo ========================================
echo   316 - Meta Ads Dashboard
echo ========================================
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado.
    echo Instale em https://python.org e tente novamente.
    pause
    exit /b 1
)

:: Criar .env se nao existir
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo AVISO: Arquivo .env criado. Edite com seu FB_ACCESS_TOKEN.
        echo.
    )
)

:: Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt --quiet

echo.
echo Iniciando dashboard em http://localhost:8501
echo Para parar: pressione CTRL+C
echo.

streamlit run dashboard.py

pause

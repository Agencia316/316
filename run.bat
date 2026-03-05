@echo off
title 316 - Meta Ads Dashboard

echo ========================================
echo   316 - Meta Ads Dashboard
echo ========================================
echo.

:: Instalar dependencias se necessario
echo Verificando dependencias...
pip install -r requirements.txt --quiet

echo.
echo Iniciando dashboard...
echo Acesse: http://localhost:8501
echo.
echo Para parar: pressione CTRL+C
echo.

streamlit run dashboard.py --server.headless false --browser.gatherUsageStats false

pause

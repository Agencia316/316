@echo off
setlocal enableextensions
chcp 65001 >nul
rem ============================================================
rem  Instala a API Juridica + painel em  D:\API JURIDICA
rem  Pre-requisitos: Python 3.10+ (python.org, marcar "Add to PATH")
rem  Uso: coloque 3-api-robo-juridico.zip na mesma pasta deste
rem  arquivo (ou passe o caminho como 1o argumento) e de duplo clique.
rem ============================================================

set "DEST=D:\API JURIDICA"
set "PAINEL_SRC=%~dp0"
set "APIZIP=%~1"
if "%APIZIP%"=="" set "APIZIP=%~dp03-api-robo-juridico.zip"

where python >nul 2>nul
if errorlevel 1 (
  echo [ERRO] Python nao encontrado. Instale em https://python.org e marque "Add python.exe to PATH".
  pause & exit /b 1
)
if not exist "%APIZIP%" (
  echo [ERRO] Nao achei o zip da API: %APIZIP%
  echo        Coloque 3-api-robo-juridico.zip ao lado deste arquivo ou passe o caminho como argumento.
  pause & exit /b 1
)
if not exist "D:\" (
  echo [ERRO] A unidade D: nao existe neste computador. Edite a linha DEST= deste arquivo.
  pause & exit /b 1
)

echo [1/6] Criando pastas em %DEST%
mkdir "%DEST%" 2>nul
mkdir "%DEST%\painel" 2>nul

echo [2/6] Copiando o painel
copy /y "%PAINEL_SRC%painel_juridico.py" "%DEST%\painel\" >nul
copy /y "%PAINEL_SRC%juridico_api.py" "%DEST%\painel\" >nul

echo [3/6] Extraindo a API
if not exist "%DEST%\api\pyproject.toml" (
  powershell -NoProfile -Command "Expand-Archive -Force -LiteralPath '%APIZIP%' -DestinationPath '%DEST%\_tmp'"
  if exist "%DEST%\_tmp\api-robo-juridico\pyproject.toml" (
    move "%DEST%\_tmp\api-robo-juridico" "%DEST%\api" >nul
  ) else (
    move "%DEST%\_tmp" "%DEST%\api" >nul
  )
  rmdir /s /q "%DEST%\_tmp" 2>nul
)
if not exist "%DEST%\api\pyproject.toml" (
  echo [ERRO] pyproject.toml nao encontrado em %DEST%\api. Confira o zip.
  pause & exit /b 1
)

echo [4/6] Criando ambiente Python e instalando (pode demorar alguns minutos)
if not exist "%DEST%\venv\Scripts\python.exe" python -m venv "%DEST%\venv"
set "PY=%DEST%\venv\Scripts\python.exe"
"%PY%" -m pip install --upgrade pip -q
"%PY%" -m pip install -q -e "%DEST%\api[api,navegador]"
if errorlevel 1 ( echo [ERRO] Falha ao instalar a API. & pause & exit /b 1 )
"%PY%" -m pip install -q streamlit plotly pandas requests python-dotenv
if errorlevel 1 ( echo [ERRO] Falha ao instalar o painel. & pause & exit /b 1 )

echo [5/6] Gerando chave interna e arquivos .env
set "KEY="
for /f %%K in ('"%PY%" -c "import secrets;print(secrets.token_urlsafe(32))"') do set "KEY=%%K"
if "%KEY%"=="" ( echo [ERRO] Nao consegui gerar a chave. & pause & exit /b 1 )
if not exist "%DEST%\api\.env" (
  > "%DEST%\api\.env" echo API_CHAVES=painel:%KEY%
  >> "%DEST%\api\.env" echo API_COOKIE_SEGURO=0
  >> "%DEST%\api\.env" echo API_BANCO=dados/api.db
  > "%DEST%\painel\.env" echo JURIDICO_API_URL=http://127.0.0.1:8000
  >> "%DEST%\painel\.env" echo JURIDICO_API_KEY=%KEY%
) else (
  echo     .env ja existe, mantido como esta.
)

echo [6/6] Criando atalhos
> "%DEST%\1-iniciar-api.bat" (
  echo @echo off
  echo cd /d "%DEST%\api"
  echo "%PY%" -m consulta_processos.cli api
  echo pause
)
> "%DEST%\2-iniciar-painel.bat" (
  echo @echo off
  echo cd /d "%DEST%\painel"
  echo "%PY%" -m streamlit run painel_juridico.py
  echo pause
)
> "%DEST%\0-testar-tela-da-api.bat" (
  echo @echo off
  echo cd /d "%DEST%\api"
  echo "%PY%" -m consulta_processos.cli web
  echo pause
)

echo.
echo ===== PRONTO =====
echo Pasta: %DEST%
echo   0-testar-tela-da-api.bat  -^> teste rapido da API (http://localhost:8765)
echo   1-iniciar-api.bat         -^> deixe aberto (http://127.0.0.1:8000)
echo   2-iniciar-painel.bat      -^> painel (http://localhost:8501)
echo A chave foi gravada nos .env; nao compartilhe esses arquivos.
pause

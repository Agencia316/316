#!/bin/bash
set -e

echo "========================================"
echo "  316 - Meta Ads Dashboard"
echo "========================================"
echo ""

# Verificar Python
if ! command -v python3 &>/dev/null; then
  echo "ERRO: Python 3 nao encontrado. Instale em https://python.org"
  exit 1
fi

# Verificar .env
if [ ! -f ".env" ]; then
  if [ -f ".env.example" ]; then
    cp .env.example .env
    echo "AVISO: Arquivo .env criado a partir do .env.example"
    echo "       Edite o .env e adicione seu FB_ACCESS_TOKEN antes de continuar."
    echo ""
    read -p "Pressione Enter para continuar mesmo assim, ou Ctrl+C para sair..."
  fi
fi

# Instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt --quiet

echo ""
echo "Iniciando dashboard em http://localhost:8501"
echo "Para parar: pressione CTRL+C"
echo ""

streamlit run dashboard.py

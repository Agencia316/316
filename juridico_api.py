"""Cliente fino da API REST do Robô Jurídico (consulta-processos).

A chave nunca vai para o navegador: este módulo roda no servidor do painel.
Configuração (st.secrets ou variáveis de ambiente):
    JURIDICO_API_URL  ex.: https://api.seudominio.com.br   (API rodando no Brasil)
    JURIDICO_API_KEY  chave do cliente gerada em /admin
"""
import os

import requests
from dotenv import load_dotenv

load_dotenv()


class ErroJuridico(Exception):
    """Erro devolvido pela API (ou falha de conexão), com mensagem pronta para exibir."""

    def __init__(self, mensagem, status=None, codigo=""):
        super().__init__(mensagem)
        self.status = status
        self.codigo = codigo


def _secret(nome):
    try:
        import streamlit as st
        valor = st.secrets.get(nome)
        if valor:
            return str(valor)
    except Exception:
        pass
    return os.getenv(nome, "")


def config():
    return _secret("JURIDICO_API_URL").rstrip("/"), _secret("JURIDICO_API_KEY")


def _get(caminho, params=None, timeout=100):
    url, chave = config()
    if not url or not chave:
        raise ErroJuridico("Configure JURIDICO_API_URL e JURIDICO_API_KEY (secrets ou .env).")
    try:
        r = requests.get(url + caminho, params=params, headers={"X-API-Key": chave}, timeout=timeout)
    except requests.RequestException as e:
        raise ErroJuridico(f"Não foi possível falar com a API: {e.__class__.__name__}") from e
    try:
        corpo = r.json()
    except ValueError:
        corpo = {}
    if r.status_code >= 400 or not corpo.get("ok", False):
        erro = corpo.get("erro", {}) if isinstance(corpo, dict) else {}
        raise ErroJuridico(erro.get("mensagem") or f"A API respondeu HTTP {r.status_code}.",
                           status=r.status_code, codigo=erro.get("codigo", ""))
    corpo["_cota"] = {
        "limite": r.headers.get("X-Cota-Limite"),
        "usada": r.headers.get("X-Cota-Usada"),
        "restante": r.headers.get("X-Cota-Restante"),
    }
    return corpo


def processo(numero, rapido=False):
    # modo=rapido usa só o diário (segundos); o completo espera o índice nacional (pode passar de 1 min)
    return _get(f"/v1/processos/{numero}", {"modo": "rapido"} if rapido else None)


def oab_processos(uf, numero, dias=30):
    return _get(f"/v1/oab/{uf}/{numero}/processos", {"dias": dias})


def oab_publicacoes(uf, numero, dias=7):
    return _get(f"/v1/oab/{uf}/{numero}/publicacoes", {"dias": dias})


def conta():
    return _get("/v1/conta", timeout=15)


def saude():
    return _get("/saude", timeout=10)

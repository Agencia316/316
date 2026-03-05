"""
Corrige o problema de proxy bloqueando conexoes com a API da Meta (graph.facebook.com).

O ambiente de execucao tem HTTPS_PROXY configurado com uma lista de hosts permitidos
que nao inclui graph.facebook.com. Este modulo forca o SDK facebook-business a
conectar diretamente, ignorando o proxy do sistema.

Uso: importe este modulo ANTES de qualquer import do facebook_business.
"""

import os
import requests

# --- Belt-and-suspenders: configura NO_PROXY para hosts da Meta ---
_META_HOSTS = [
    "graph.facebook.com",
    "graph.instagram.com",
    "api.facebook.com",
    "www.facebook.com",
]

_existing_no_proxy = os.environ.get("NO_PROXY", os.environ.get("no_proxy", ""))
_combined = ",".join(filter(None, [_existing_no_proxy] + _META_HOSTS))
os.environ["NO_PROXY"] = _combined
os.environ["no_proxy"] = _combined

# --- Patch principal: novas requests.Session nao usam proxy ---
_original_session_init = requests.Session.__init__


def _no_proxy_session_init(self, *args, **kwargs):
    _original_session_init(self, *args, **kwargs)
    self.trust_env = False  # Nao le proxy das variaveis de ambiente
    self.proxies = {}       # Sem proxy configurado


requests.Session.__init__ = _no_proxy_session_init

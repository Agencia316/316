"""
Corrige o problema de proxy bloqueando conexoes com a API da Meta (graph.facebook.com).

Aplica o patch APENAS quando o ambiente tiver um proxy configurado (GLOBAL_AGENT_HTTP_PROXY
ou HTTPS_PROXY). No Streamlit Cloud e outros ambientes sem proxy, este modulo e inofensivo.
"""

import os

_proxy = os.environ.get("GLOBAL_AGENT_HTTP_PROXY") or os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")

if _proxy:
    import requests

    # Adiciona hosts da Meta ao NO_PROXY para que nao passem pelo proxy
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

    # Patch apenas quando proxy estiver ativo: novas sessions da facebook_business nao usam proxy
    _original_session_init = requests.Session.__init__

    def _no_proxy_session_init(self, *args, **kwargs):
        _original_session_init(self, *args, **kwargs)
        self.trust_env = False
        self.proxies = {}

    requests.Session.__init__ = _no_proxy_session_init

"""Painel jurídico para embutir no CRM Umbra (iframe).

    streamlit run painel_juridico.py

Embutir no Umbra:  <iframe src="https://SEU-PAINEL/?embed=true&oab_uf=MG&oab_numero=123456&processo=..."></iframe>
Parâmetros de URL opcionais: processo, oab_uf, oab_numero, dias — o CRM pode pré-preencher por cliente.
"""
import re
from collections import Counter

import pandas as pd
import plotly.express as px
import streamlit as st

import juridico_api as api

st.set_page_config(page_title="Painel Jurídico", page_icon="⚖️", layout="wide")

UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB",
       "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]
qp = st.query_params


def _qp(nome, padrao=""):
    return qp.get(nome, padrao)


@st.cache_data(ttl=1800, show_spinner=False)
def _processo(numero, rapido):
    return api.processo(numero, rapido)


@st.cache_data(ttl=900, show_spinner=False)
def _oab(uf, numero, dias):
    return api.oab_processos(uf, numero, dias), api.oab_publicacoes(uf, numero, dias)


def _erro(e):
    if e.status == 402:
        st.error("Cota mensal de consultas esgotada. Fale com o administrador.")
    elif e.status == 429:
        st.warning("Muitas consultas seguidas. Aguarde um minuto e tente de novo.")
    elif e.status == 503:
        st.warning("A fonte oficial está fora do ar. Tente de novo em instantes.")
    else:
        st.error(str(e))


def _rodape_cota(corpo):
    c = corpo.get("_cota", {})
    if c.get("restante") is not None:
        st.caption(f"Cota do mês: {c['usada']} de {c['limite']} usadas · {c['restante']} restantes")


st.title("⚖️ Painel Jurídico")
aba_proc, aba_oab, aba_conta = st.tabs(["Processo", "Advogado (OAB)", "Conta"])

# ── Processo ─────────────────────────────────────────────────────────────────
with aba_proc:
    c1, c2 = st.columns([4, 1])
    numero = c1.text_input("Número do processo (CNJ)", value=_qp("processo"),
                           placeholder="0000000-00.0000.0.00.0000")
    rapido = c2.checkbox("Modo rápido", value=True,
                         help="Só diário (segundos). Desmarque para o histórico completo (pode levar mais de 1 min).")
    if numero and st.button("Consultar", type="primary", key="b_proc") or (numero and _qp("processo")):
        try:
            with st.spinner("Consultando…"):
                r = _processo(numero.strip(), rapido)
            p = r["processo"]
            st.subheader(p["titulo"] or p["numero"])
            st.caption(f"{p['numero']} · {p['tribunal']} · {p['classe']}")
            k = st.columns(4)
            k[0].metric("Movimentações", p["totais"]["movimentacoes"])
            k[1].metric("Publicações", p["totais"]["publicacoes"])
            k[2].metric("Última movimentação", p["data_ultima_movimentacao_formatada"] or "—")
            k[3].metric("Valor da causa", p["valor_causa_formatado"] or "—")
            st.write(f"**Órgão:** {p['orgao_julgador'] or '—'} · **Assunto:** {p['assunto'] or '—'} · "
                     f"**Situação:** {p['situacao'] or '—'}")
            for av in r.get("avisos", []):
                st.info(av)
            polos = p["polos"]
            cA, cP = st.columns(2)
            for col, titulo, partes in ((cA, "Polo ativo", polos["ativo"]), (cP, "Polo passivo", polos["passivo"])):
                with col:
                    st.markdown(f"**{titulo}**")
                    for parte in partes:
                        advs = ", ".join(a["oab"] or a["nome"] for a in parte["advogados"])
                        st.write(f"• {parte['nome']}" + (f" — {advs}" if advs else ""))
            if p["movimentacoes"]:
                st.markdown("**Movimentações**")
                st.dataframe(pd.DataFrame(p["movimentacoes"])[["data_formatada", "tipo", "descricao", "complemento"]]
                             .rename(columns={"data_formatada": "Data", "tipo": "Tipo",
                                              "descricao": "Descrição", "complemento": "Complemento"}),
                             hide_index=True, use_container_width=True)
            for pub in p["publicacoes"][:10]:
                with st.expander(f"{pub['data_formatada']} · {pub['tipo_comunicacao']} · {pub['orgao']}"):
                    st.write(pub["texto"])
                    if pub["link"]:
                        st.link_button("Abrir no diário", pub["link"])
            _rodape_cota(r)
        except api.ErroJuridico as e:
            _erro(e)

# ── OAB ──────────────────────────────────────────────────────────────────────
with aba_oab:
    c1, c2, c3 = st.columns([1, 2, 2])
    uf_pad = _qp("oab_uf", "MG").upper()
    uf = c1.selectbox("UF", UFS, index=UFS.index(uf_pad) if uf_pad in UFS else UFS.index("MG"))
    oab = c2.text_input("Nº OAB", value=_qp("oab_numero"))
    dias = c3.slider("Período (dias)", 1, 90, int(_qp("dias", 30)) if str(_qp("dias", 30)).isdigit() else 30)
    if oab and (st.button("Buscar", type="primary", key="b_oab") or _qp("oab_numero")):
        num = re.sub(r"\D", "", oab)
        try:
            with st.spinner("Lendo o diário…"):
                rp, rb = _oab(uf, num, dias)
            if rp.get("parcial"):
                st.warning(rp.get("aviso") or "Resultado parcial: reduza o período.")
            pubs = pd.DataFrame(rb["publicacoes"])
            procs = pd.DataFrame(rp["processos"])
            k = st.columns(3)
            k[0].metric("Processos com publicação", rp["total"])
            k[1].metric("Publicações", rb["total"])
            k[2].metric("Tribunais", pubs["tribunal"].nunique() if not pubs.empty else 0)
            if not pubs.empty:
                g1, g2 = st.columns(2)
                por_dia = pubs.groupby("data_formatada").size().reset_index(name="Publicações")
                g1.plotly_chart(px.bar(por_dia, x="data_formatada", y="Publicações", title="Publicações por dia"),
                                use_container_width=True)
                por_trib = pd.DataFrame(Counter(pubs["tribunal"]).most_common(), columns=["Tribunal", "Publicações"])
                g2.plotly_chart(px.pie(por_trib, names="Tribunal", values="Publicações", title="Por tribunal"),
                                use_container_width=True)
                st.markdown("**Publicações (controle de prazo)**")
                st.dataframe(pubs[["data_formatada", "numero_processo", "tribunal", "tipo_comunicacao", "orgao"]]
                             .rename(columns={"data_formatada": "Data", "numero_processo": "Processo",
                                              "tribunal": "Tribunal", "tipo_comunicacao": "Tipo",
                                              "orgao": "Órgão"}),
                             hide_index=True, use_container_width=True)
            if not procs.empty:
                st.markdown("**Processos**")
                st.dataframe(procs[["numero", "titulo", "tribunal", "classe", "data_ultima_movimentacao_formatada",
                                    "publicacoes"]]
                             .rename(columns={"numero": "Número", "titulo": "Título", "tribunal": "Tribunal",
                                              "classe": "Classe", "publicacoes": "Publicações",
                                              "data_ultima_movimentacao_formatada": "Últ. movimentação"}),
                             hide_index=True, use_container_width=True)
            _rodape_cota(rb)
        except api.ErroJuridico as e:
            _erro(e)

# ── Conta ────────────────────────────────────────────────────────────────────
with aba_conta:
    if st.button("Atualizar", key="b_conta"):
        try:
            c = api.conta()
            st.json({k: v for k, v in c.items() if k not in ("ok", "_cota")})
        except api.ErroJuridico as e:
            _erro(e)
    url, chave = api.config()
    st.caption(f"API: {url or 'não configurada'} · chave: {'configurada' if chave else 'ausente'}")

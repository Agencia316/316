import os
import proxy_fix  # noqa: F401 - deve vir antes de facebook_business
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.user import User

load_dotenv()

ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

st.set_page_config(
    page_title="316 — Dashboard de Campanhas",
    page_icon="📊",
    layout="wide",
)

# ── helpers ──────────────────────────────────────────────────────────────────

def fmt_currency(value, currency="BRL"):
    symbol = "R$" if currency == "BRL" else "$"
    return f"{symbol} {float(value):,.2f}"


def extract_action(actions, action_type):
    if not actions:
        return 0
    for a in actions:
        if a.get("action_type") == action_type:
            return int(a.get("value", 0))
    return 0


def extract_cost_per_action(cpa_list, action_type):
    if not cpa_list:
        return None
    for a in cpa_list:
        if a.get("action_type") == action_type:
            v = a.get("value")
            return float(v) if v else None
    return None


# ── API ───────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner="Buscando contas...")
def load_accounts():
    FacebookAdsApi.init(access_token=ACCESS_TOKEN)
    me = User(fbid="me")
    return list(me.get_ad_accounts(fields=["id", "name", "currency", "account_status"]))


@st.cache_data(ttl=300, show_spinner="Buscando campanhas...")
def load_campaigns(ad_account_id, date_preset):
    account = AdAccount(ad_account_id)
    insights = account.get_insights(
        fields=[
            "campaign_id",
            "campaign_name",
            "impressions",
            "clicks",
            "reach",
            "spend",
            "ctr",
            "cpc",
            "cpm",
            "frequency",
            "actions",
            "cost_per_action_type",
            "objective",
        ],
        params={
            "date_preset": date_preset,
            "level": "campaign",
            "sort": ["spend_descending"],
        },
    )
    rows = []
    for c in insights:
        actions = c.get("actions", [])
        cpa_list = c.get("cost_per_action_type", [])
        leads = extract_action(actions, "lead") or extract_action(actions, "onsite_conversion.lead_grouped")
        purchases = extract_action(actions, "purchase")
        link_clicks = extract_action(actions, "link_click")
        cpl = extract_cost_per_action(cpa_list, "lead")
        cpp = extract_cost_per_action(cpa_list, "purchase")
        rows.append({
            "Campanha": c.get("campaign_name", ""),
            "Gasto": float(c.get("spend", 0)),
            "Impressões": int(c.get("impressions", 0)),
            "Alcance": int(c.get("reach", 0)),
            "Cliques": int(c.get("clicks", 0)),
            "CTR (%)": float(c.get("ctr", 0)),
            "CPC": float(c.get("cpc", 0)) if c.get("cpc") else 0,
            "CPM": float(c.get("cpm", 0)) if c.get("cpm") else 0,
            "Frequência": float(c.get("frequency", 0)) if c.get("frequency") else 0,
            "Leads": leads,
            "Compras": purchases,
            "Cliques no Link": link_clicks,
            "CPL": cpl or 0,
            "CPP": cpp or 0,
            "Objetivo": c.get("objective", ""),
        })
    return pd.DataFrame(rows)


# ── layout ────────────────────────────────────────────────────────────────────

st.title("📊 316 — Dashboard de Campanhas Meta Ads")

if not ACCESS_TOKEN:
    st.error("Token não encontrado. Verifique o arquivo .env.")
    st.stop()

try:
    accounts = load_accounts()
except Exception as e:
    st.error(f"Erro ao conectar na API: {e}")
    st.stop()

status_map = {1: "Ativa", 2: "Desativada", 3: "Suspensa", 7: "Pendente", 9: "Em revisão"}
account_labels = {
    acc["id"]: f"{acc.get('name', 'Sem nome')} ({status_map.get(acc.get('account_status'), '?')})"
    for acc in accounts
}
account_currencies = {acc["id"]: acc.get("currency", "BRL") for acc in accounts}

# sidebar
with st.sidebar:
    st.header("Filtros")
    selected_id = st.selectbox("Conta de anúncio", options=list(account_labels.keys()), format_func=lambda x: account_labels[x])
    date_preset = st.selectbox(
        "Período",
        options=["last_7d", "last_14d", "last_30d", "last_90d", "this_month", "last_month"],
        index=2,
        format_func=lambda x: {
            "last_7d": "Últimos 7 dias",
            "last_14d": "Últimos 14 dias",
            "last_30d": "Últimos 30 dias",
            "last_90d": "Últimos 90 dias",
            "this_month": "Este mês",
            "last_month": "Mês passado",
        }[x],
    )
    if st.button("🔄 Atualizar dados"):
        st.cache_data.clear()
        st.rerun()

currency = account_currencies[selected_id]

try:
    df = load_campaigns(selected_id, date_preset)
except Exception as e:
    st.error(f"Erro ao buscar campanhas: {e}")
    st.stop()

if df.empty:
    st.warning("Nenhuma campanha com dados no período selecionado.")
    st.stop()

# ── KPIs ──────────────────────────────────────────────────────────────────────

total_spend = df["Gasto"].sum()
total_impressions = df["Impressões"].sum()
total_clicks = df["Cliques"].sum()
total_reach = df["Alcance"].sum()
total_leads = df["Leads"].sum()
total_purchases = df["Compras"].sum()
avg_ctr = (total_clicks / total_impressions * 100) if total_impressions else 0
avg_cpm = (total_spend / total_impressions * 1000) if total_impressions else 0
avg_cpl = (total_spend / total_leads) if total_leads else 0
avg_cpp = (total_spend / total_purchases) if total_purchases else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Gasto", fmt_currency(total_spend, currency))
col2.metric("👥 Alcance", f"{int(total_reach):,}")
col3.metric("👁️ Impressões", f"{int(total_impressions):,}")
col4.metric("🖱️ Cliques", f"{int(total_clicks):,}")

col5, col6, col7, col8 = st.columns(4)
col5.metric("📈 CTR Médio", f"{avg_ctr:.2f}%")
col6.metric("📢 CPM Médio", fmt_currency(avg_cpm, currency))
if total_leads:
    col7.metric("🎯 Leads", f"{int(total_leads):,}")
    col8.metric("💡 CPL Médio", fmt_currency(avg_cpl, currency))
elif total_purchases:
    col7.metric("🛒 Compras", f"{int(total_purchases):,}")
    col8.metric("💡 CPP Médio", fmt_currency(avg_cpp, currency))

st.divider()

# ── gráficos ──────────────────────────────────────────────────────────────────

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Gasto por Campanha")
    fig_spend = px.bar(
        df.sort_values("Gasto"),
        x="Gasto",
        y="Campanha",
        orientation="h",
        color="Gasto",
        color_continuous_scale="Blues",
        text_auto=".2f",
    )
    fig_spend.update_layout(showlegend=False, coloraxis_showscale=False, height=400)
    st.plotly_chart(fig_spend, use_container_width=True)

with col_b:
    st.subheader("CTR por Campanha")
    fig_ctr = px.bar(
        df.sort_values("CTR (%)"),
        x="CTR (%)",
        y="Campanha",
        orientation="h",
        color="CTR (%)",
        color_continuous_scale="Greens",
        text_auto=".2f",
    )
    fig_ctr.update_layout(showlegend=False, coloraxis_showscale=False, height=400)
    st.plotly_chart(fig_ctr, use_container_width=True)

col_c, col_d = st.columns(2)

with col_c:
    st.subheader("Alcance vs Impressões")
    fig_reach = go.Figure()
    fig_reach.add_trace(go.Bar(name="Alcance", x=df["Campanha"], y=df["Alcance"], marker_color="#636EFA"))
    fig_reach.add_trace(go.Bar(name="Impressões", x=df["Campanha"], y=df["Impressões"], marker_color="#EF553B"))
    fig_reach.update_layout(barmode="group", height=400, xaxis_tickangle=-30)
    st.plotly_chart(fig_reach, use_container_width=True)

with col_d:
    st.subheader("CPC vs CPM")
    fig_cpc = go.Figure()
    fig_cpc.add_trace(go.Bar(name="CPC", x=df["Campanha"], y=df["CPC"], marker_color="#00CC96"))
    fig_cpc.add_trace(go.Bar(name="CPM", x=df["Campanha"], y=df["CPM"], marker_color="#AB63FA"))
    fig_cpc.update_layout(barmode="group", height=400, xaxis_tickangle=-30)
    st.plotly_chart(fig_cpc, use_container_width=True)

if total_leads > 0:
    st.subheader("Leads e CPL por Campanha")
    df_leads = df[df["Leads"] > 0].copy()
    col_e, col_f = st.columns(2)
    with col_e:
        fig_leads = px.pie(df_leads, values="Leads", names="Campanha", title="Distribuição de Leads")
        st.plotly_chart(fig_leads, use_container_width=True)
    with col_f:
        fig_cpl = px.bar(df_leads.sort_values("CPL"), x="Campanha", y="CPL", color="CPL",
                         color_continuous_scale="Reds", text_auto=".2f", title="CPL por Campanha")
        fig_cpl.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_cpl, use_container_width=True)

st.divider()

# ── tabela ────────────────────────────────────────────────────────────────────

st.subheader("Tabela Completa")

display_cols = ["Campanha", "Gasto", "Alcance", "Impressões", "Cliques", "CTR (%)", "CPC", "CPM", "Frequência", "Leads", "CPL", "Compras", "CPP"]
st.dataframe(
    df[display_cols].style.format({
        "Gasto": "{:.2f}",
        "CPC": "{:.2f}",
        "CPM": "{:.2f}",
        "CTR (%)": "{:.2f}",
        "Frequência": "{:.1f}",
        "CPL": "{:.2f}",
        "CPP": "{:.2f}",
    }).background_gradient(subset=["Gasto"], cmap="Blues")
     .background_gradient(subset=["CTR (%)"], cmap="Greens"),
    use_container_width=True,
    height=400,
)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Exportar CSV", csv, "campanhas.csv", "text/csv")

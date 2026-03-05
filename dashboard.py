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

st.set_page_config(page_title="316 — Meta Ads 360°", page_icon="📊", layout="wide")

# ── helpers ───────────────────────────────────────────────────────────────────

def fmt(value, currency="BRL"):
    symbol = "R$" if currency == "BRL" else "$"
    try:
        return f"{symbol} {float(value):,.2f}"
    except Exception:
        return "–"

def safe_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default

def safe_int(v, default=0):
    try:
        return int(v)
    except Exception:
        return default

def extract_action(actions, action_type):
    if not actions:
        return 0
    for a in actions:
        if a.get("action_type") == action_type:
            return safe_int(a.get("value", 0))
    return 0

def extract_cpa(cpa_list, action_type):
    if not cpa_list:
        return 0.0
    for a in cpa_list:
        if a.get("action_type") == action_type:
            return safe_float(a.get("value", 0))
    return 0.0

def extract_all_actions(actions):
    if not actions:
        return {}
    return {a["action_type"]: safe_int(a.get("value", 0)) for a in actions}

STATUS_MAP = {1: "Ativa", 2: "Desativada", 3: "Suspensa", 7: "Pendente", 9: "Em revisão"}
CAMPAIGN_STATUS = {"ACTIVE": "Ativa", "PAUSED": "Pausada", "ARCHIVED": "Arquivada",
                   "DELETED": "Excluída", "IN_PROCESS": "Processando", "WITH_ISSUES": "Com problemas"}

PERIOD_LABELS = {
    "last_7d": "Últimos 7 dias", "last_14d": "Últimos 14 dias",
    "last_30d": "Últimos 30 dias", "last_90d": "Últimos 90 dias",
    "this_month": "Este mês", "last_month": "Mês passado",
}

# ── API calls ─────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner="Buscando contas...")
def load_accounts():
    FacebookAdsApi.init(access_token=ACCESS_TOKEN)
    me = User(fbid="me")
    return [dict(a) for a in me.get_ad_accounts(fields=[
        "id", "name", "currency", "account_status",
        "amount_spent", "balance", "spend_cap",
        "timezone_name", "business_name",
    ])]

@st.cache_data(ttl=300, show_spinner="Buscando campanhas...")
def load_campaigns(account_id, date_preset):
    account = AdAccount(account_id)
    insights = account.get_insights(
        fields=[
            "campaign_id", "campaign_name", "objective",
            "impressions", "clicks", "reach", "spend",
            "ctr", "cpc", "cpm", "cpp", "frequency",
            "actions", "cost_per_action_type",
            "unique_clicks", "unique_ctr",
            "video_play_actions", "video_thruplay_watched_actions",
            "outbound_clicks", "outbound_clicks_ctr",
        ],
        params={"date_preset": date_preset, "level": "campaign", "sort": ["spend_descending"]},
    )
    rows = []
    for c in insights:
        actions = c.get("actions", [])
        cpa_list = c.get("cost_per_action_type", [])
        leads = extract_action(actions, "lead") or extract_action(actions, "onsite_conversion.lead_grouped")
        purchases = extract_action(actions, "purchase")
        link_clicks = extract_action(actions, "link_click")
        outbound = 0
        if c.get("outbound_clicks"):
            outbound = sum(safe_int(o.get("value", 0)) for o in c["outbound_clicks"])
        video_plays = 0
        if c.get("video_play_actions"):
            video_plays = sum(safe_int(v.get("value", 0)) for v in c["video_play_actions"])
        thruplays = 0
        if c.get("video_thruplay_watched_actions"):
            thruplays = sum(safe_int(v.get("value", 0)) for v in c["video_thruplay_watched_actions"])
        spend = safe_float(c.get("spend", 0))
        rows.append({
            "ID": c.get("campaign_id", ""),
            "Campanha": c.get("campaign_name", ""),
            "Objetivo": c.get("objective", ""),
            "Gasto": spend,
            "Impressões": safe_int(c.get("impressions", 0)),
            "Alcance": safe_int(c.get("reach", 0)),
            "Cliques": safe_int(c.get("clicks", 0)),
            "Cliques Únicos": safe_int(c.get("unique_clicks", 0)),
            "CTR (%)": safe_float(c.get("ctr", 0)),
            "CTR Único (%)": safe_float(c.get("unique_ctr", 0)),
            "CPC": safe_float(c.get("cpc", 0)),
            "CPM": safe_float(c.get("cpm", 0)),
            "CPP": safe_float(c.get("cpp", 0)),
            "Frequência": safe_float(c.get("frequency", 0)),
            "Cliques no Link": link_clicks,
            "Cliques Externos": outbound,
            "Leads": leads,
            "CPL": extract_cpa(cpa_list, "lead") or extract_cpa(cpa_list, "onsite_conversion.lead_grouped"),
            "Compras": purchases,
            "CPP Compra": extract_cpa(cpa_list, "purchase"),
            "Video Views": video_plays,
            "ThruPlays": thruplays,
            "Todas Ações": extract_all_actions(actions),
        })
    return pd.DataFrame(rows)

@st.cache_data(ttl=300, show_spinner="Buscando conjuntos de anúncios...")
def load_adsets(account_id, date_preset):
    account = AdAccount(account_id)
    insights = account.get_insights(
        fields=[
            "adset_id", "adset_name", "campaign_name",
            "impressions", "clicks", "reach", "spend",
            "ctr", "cpc", "cpm", "frequency",
            "actions", "cost_per_action_type",
            "unique_clicks", "unique_ctr",
        ],
        params={"date_preset": date_preset, "level": "adset", "sort": ["spend_descending"]},
    )
    rows = []
    for c in insights:
        actions = c.get("actions", [])
        cpa_list = c.get("cost_per_action_type", [])
        leads = extract_action(actions, "lead") or extract_action(actions, "onsite_conversion.lead_grouped")
        purchases = extract_action(actions, "purchase")
        spend = safe_float(c.get("spend", 0))
        rows.append({
            "ID": c.get("adset_id", ""),
            "Conjunto": c.get("adset_name", ""),
            "Campanha": c.get("campaign_name", ""),
            "Gasto": spend,
            "Impressões": safe_int(c.get("impressions", 0)),
            "Alcance": safe_int(c.get("reach", 0)),
            "Cliques": safe_int(c.get("clicks", 0)),
            "CTR (%)": safe_float(c.get("ctr", 0)),
            "CPC": safe_float(c.get("cpc", 0)),
            "CPM": safe_float(c.get("cpm", 0)),
            "Frequência": safe_float(c.get("frequency", 0)),
            "Leads": leads,
            "CPL": extract_cpa(cpa_list, "lead"),
            "Compras": purchases,
            "CPP": extract_cpa(cpa_list, "purchase"),
        })
    return pd.DataFrame(rows)

@st.cache_data(ttl=300, show_spinner="Buscando anúncios...")
def load_ads(account_id, date_preset):
    account = AdAccount(account_id)
    insights = account.get_insights(
        fields=[
            "ad_id", "ad_name", "adset_name", "campaign_name",
            "impressions", "clicks", "reach", "spend",
            "ctr", "cpc", "cpm", "frequency",
            "actions", "cost_per_action_type",
            "unique_clicks", "unique_ctr",
            "video_play_actions", "video_thruplay_watched_actions",
        ],
        params={"date_preset": date_preset, "level": "ad", "sort": ["spend_descending"]},
    )
    rows = []
    for c in insights:
        actions = c.get("actions", [])
        cpa_list = c.get("cost_per_action_type", [])
        leads = extract_action(actions, "lead") or extract_action(actions, "onsite_conversion.lead_grouped")
        purchases = extract_action(actions, "purchase")
        video_plays = 0
        if c.get("video_play_actions"):
            video_plays = sum(safe_int(v.get("value", 0)) for v in c["video_play_actions"])
        thruplays = 0
        if c.get("video_thruplay_watched_actions"):
            thruplays = sum(safe_int(v.get("value", 0)) for v in c["video_thruplay_watched_actions"])
        spend = safe_float(c.get("spend", 0))
        rows.append({
            "ID": c.get("ad_id", ""),
            "Anúncio": c.get("ad_name", ""),
            "Conjunto": c.get("adset_name", ""),
            "Campanha": c.get("campaign_name", ""),
            "Gasto": spend,
            "Impressões": safe_int(c.get("impressions", 0)),
            "Alcance": safe_int(c.get("reach", 0)),
            "Cliques": safe_int(c.get("clicks", 0)),
            "Cliques Únicos": safe_int(c.get("unique_clicks", 0)),
            "CTR (%)": safe_float(c.get("ctr", 0)),
            "CPC": safe_float(c.get("cpc", 0)),
            "CPM": safe_float(c.get("cpm", 0)),
            "Frequência": safe_float(c.get("frequency", 0)),
            "Leads": leads,
            "CPL": extract_cpa(cpa_list, "lead"),
            "Compras": purchases,
            "CPP": extract_cpa(cpa_list, "purchase"),
            "Video Views": video_plays,
            "ThruPlays": thruplays,
        })
    return pd.DataFrame(rows)

@st.cache_data(ttl=300, show_spinner="Buscando breakdown por gênero/idade...")
def load_demographics(account_id, date_preset):
    account = AdAccount(account_id)
    age = account.get_insights(
        fields=["impressions", "clicks", "spend", "reach", "ctr", "actions"],
        params={"date_preset": date_preset, "level": "account", "breakdowns": ["age"]},
    )
    gender = account.get_insights(
        fields=["impressions", "clicks", "spend", "reach", "ctr", "actions"],
        params={"date_preset": date_preset, "level": "account", "breakdowns": ["gender"]},
    )
    age_gender = account.get_insights(
        fields=["impressions", "clicks", "spend", "reach", "ctr"],
        params={"date_preset": date_preset, "level": "account", "breakdowns": ["age", "gender"]},
    )
    def parse(rows, key):
        result = []
        for r in rows:
            leads = extract_action(r.get("actions", []), "lead") or extract_action(r.get("actions", []), "onsite_conversion.lead_grouped")
            result.append({
                key: r.get(key, ""),
                "Impressões": safe_int(r.get("impressions", 0)),
                "Alcance": safe_int(r.get("reach", 0)),
                "Cliques": safe_int(r.get("clicks", 0)),
                "Gasto": safe_float(r.get("spend", 0)),
                "CTR (%)": safe_float(r.get("ctr", 0)),
                "Leads": leads,
            })
        return pd.DataFrame(result)

    df_age = parse(list(age), "age")
    df_gender = parse(list(gender), "gender")
    df_ag_raw = []
    for r in list(age_gender):
        df_ag_raw.append({
            "age": r.get("age", ""),
            "gender": r.get("gender", ""),
            "Impressões": safe_int(r.get("impressions", 0)),
            "Gasto": safe_float(r.get("spend", 0)),
        })
    df_ag = pd.DataFrame(df_ag_raw)
    return df_age, df_gender, df_ag

@st.cache_data(ttl=300, show_spinner="Buscando breakdown por posicionamento...")
def load_placement(account_id, date_preset):
    account = AdAccount(account_id)
    rows = account.get_insights(
        fields=["impressions", "clicks", "spend", "reach", "ctr", "cpc", "cpm", "actions"],
        params={"date_preset": date_preset, "level": "account",
                "breakdowns": ["publisher_platform", "platform_position"]},
    )
    result = []
    for r in list(rows):
        leads = extract_action(r.get("actions", []), "lead") or extract_action(r.get("actions", []), "onsite_conversion.lead_grouped")
        result.append({
            "Plataforma": r.get("publisher_platform", ""),
            "Posição": r.get("platform_position", ""),
            "Impressões": safe_int(r.get("impressions", 0)),
            "Alcance": safe_int(r.get("reach", 0)),
            "Cliques": safe_int(r.get("clicks", 0)),
            "Gasto": safe_float(r.get("spend", 0)),
            "CTR (%)": safe_float(r.get("ctr", 0)),
            "CPC": safe_float(r.get("cpc", 0)),
            "CPM": safe_float(r.get("cpm", 0)),
            "Leads": leads,
        })
    return pd.DataFrame(result)

@st.cache_data(ttl=300, show_spinner="Buscando evolução diária...")
def load_daily(account_id, date_preset):
    account = AdAccount(account_id)
    rows = account.get_insights(
        fields=["impressions", "clicks", "spend", "reach", "ctr", "cpm", "actions", "date_start"],
        params={"date_preset": date_preset, "level": "account",
                "time_increment": 1, "sort": ["date_start_ascending"]},
    )
    result = []
    for r in list(rows):
        leads = extract_action(r.get("actions", []), "lead") or extract_action(r.get("actions", []), "onsite_conversion.lead_grouped")
        purchases = extract_action(r.get("actions", []), "purchase")
        result.append({
            "Data": r.get("date_start", ""),
            "Gasto": safe_float(r.get("spend", 0)),
            "Impressões": safe_int(r.get("impressions", 0)),
            "Alcance": safe_int(r.get("reach", 0)),
            "Cliques": safe_int(r.get("clicks", 0)),
            "CTR (%)": safe_float(r.get("ctr", 0)),
            "CPM": safe_float(r.get("cpm", 0)),
            "Leads": leads,
            "Compras": purchases,
        })
    df = pd.DataFrame(result)
    if not df.empty:
        df["Data"] = pd.to_datetime(df["Data"])
    return df

# ── layout ────────────────────────────────────────────────────────────────────

st.title("📊 316 — Meta Ads 360° — Análise Completa")

if not ACCESS_TOKEN:
    st.error("Token não encontrado. Verifique o arquivo .env.")
    st.stop()

try:
    accounts = load_accounts()
except Exception as e:
    st.error(f"Erro ao conectar na API: {e}")
    st.stop()

account_labels = {
    acc["id"]: f"{acc.get('name', 'Sem nome')} ({STATUS_MAP.get(acc.get('account_status'), '?')})"
    for acc in accounts
}
account_map = {acc["id"]: acc for acc in accounts}

with st.sidebar:
    st.header("Filtros")
    selected_id = st.selectbox(
        "Conta de anúncio",
        options=list(account_labels.keys()),
        format_func=lambda x: account_labels[x],
    )
    date_preset = st.selectbox(
        "Período",
        options=list(PERIOD_LABELS.keys()),
        index=2,
        format_func=lambda x: PERIOD_LABELS[x],
    )
    if st.button("🔄 Atualizar dados"):
        st.cache_data.clear()
        st.rerun()

acc_info = account_map[selected_id]
currency = acc_info.get("currency", "BRL")

# ── abas ─────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏦 Conta",
    "📣 Campanhas",
    "🗂️ Conjuntos",
    "🎨 Anúncios",
    "👥 Público",
    "📍 Posicionamento",
    "📅 Evolução Diária",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — CONTA
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Informações da Conta")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Nome", acc_info.get("name", "–"))
    c2.metric("Status", STATUS_MAP.get(acc_info.get("account_status"), "?"))
    c3.metric("Moeda", currency)
    c4.metric("Fuso Horário", acc_info.get("timezone_name", "–"))

    c5, c6, c7, c8 = st.columns(4)
    spent = safe_float(acc_info.get("amount_spent", 0)) / 100
    balance = safe_float(acc_info.get("balance", 0)) / 100
    spend_cap = safe_float(acc_info.get("spend_cap", 0)) / 100
    c5.metric("Total Gasto (histórico)", fmt(spent, currency))
    c6.metric("Saldo", fmt(balance, currency))
    c7.metric("Limite de Gasto", fmt(spend_cap, currency) if spend_cap else "Sem limite")
    c8.metric("Business", acc_info.get("business_name", "–"))

    st.divider()
    st.subheader("Todas as Contas Disponíveis")
    df_accs = pd.DataFrame([{
        "Nome": a.get("name", ""),
        "ID": a["id"],
        "Status": STATUS_MAP.get(a.get("account_status"), "?"),
        "Moeda": a.get("currency", ""),
        "Total Gasto": safe_float(a.get("amount_spent", 0)) / 100,
        "Business": a.get("business_name", "–"),
    } for a in accounts])
    st.dataframe(df_accs, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CAMPANHAS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    try:
        df_camp = load_campaigns(selected_id, date_preset)
    except Exception as e:
        st.error(f"Erro: {e}")
        st.stop()

    if df_camp.empty:
        st.warning("Nenhuma campanha no período.")
    else:
        total_spend = df_camp["Gasto"].sum()
        total_imp = df_camp["Impressões"].sum()
        total_clicks = df_camp["Cliques"].sum()
        total_reach = df_camp["Alcance"].sum()
        total_leads = df_camp["Leads"].sum()
        total_purchases = df_camp["Compras"].sum()
        avg_ctr = (total_clicks / total_imp * 100) if total_imp else 0
        avg_cpm = (total_spend / total_imp * 1000) if total_imp else 0
        avg_freq = df_camp["Frequência"].mean()

        st.subheader("KPIs Gerais")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("💰 Total Gasto", fmt(total_spend, currency))
        k2.metric("👥 Alcance", f"{int(total_reach):,}")
        k3.metric("👁️ Impressões", f"{int(total_imp):,}")
        k4.metric("🖱️ Cliques", f"{int(total_clicks):,}")

        k5, k6, k7, k8 = st.columns(4)
        k5.metric("📈 CTR Médio", f"{avg_ctr:.2f}%")
        k6.metric("📢 CPM Médio", fmt(avg_cpm, currency))
        k7.metric("🔁 Freq. Média", f"{avg_freq:.1f}x")
        if total_leads:
            k8.metric("🎯 CPL Médio", fmt(total_spend / total_leads, currency))
        elif total_purchases:
            k8.metric("🛒 CPP Médio", fmt(total_spend / total_purchases, currency))

        if total_leads:
            k9, k10 = st.columns(2)
            k9.metric("🎯 Total Leads", f"{int(total_leads):,}")
            k10.metric("🛒 Total Compras", f"{int(total_purchases):,}")

        st.divider()

        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Gasto por Campanha")
            fig = px.bar(df_camp.sort_values("Gasto"), x="Gasto", y="Campanha",
                         orientation="h", color="Gasto", color_continuous_scale="Blues", text_auto=".2f")
            fig.update_layout(coloraxis_showscale=False, height=420)
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.subheader("CTR por Campanha")
            fig = px.bar(df_camp.sort_values("CTR (%)"), x="CTR (%)", y="Campanha",
                         orientation="h", color="CTR (%)", color_continuous_scale="Greens", text_auto=".2f")
            fig.update_layout(coloraxis_showscale=False, height=420)
            st.plotly_chart(fig, use_container_width=True)

        col_c, col_d = st.columns(2)
        with col_c:
            st.subheader("Alcance vs Impressões")
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Alcance", x=df_camp["Campanha"], y=df_camp["Alcance"], marker_color="#636EFA"))
            fig.add_trace(go.Bar(name="Impressões", x=df_camp["Campanha"], y=df_camp["Impressões"], marker_color="#EF553B"))
            fig.update_layout(barmode="group", height=380, xaxis_tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)

        with col_d:
            st.subheader("CPC vs CPM")
            fig = go.Figure()
            fig.add_trace(go.Bar(name="CPC", x=df_camp["Campanha"], y=df_camp["CPC"], marker_color="#00CC96"))
            fig.add_trace(go.Bar(name="CPM", x=df_camp["Campanha"], y=df_camp["CPM"], marker_color="#AB63FA"))
            fig.update_layout(barmode="group", height=380, xaxis_tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)

        if df_camp["Video Views"].sum() > 0:
            st.subheader("Video Views vs ThruPlays")
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Video Views", x=df_camp["Campanha"], y=df_camp["Video Views"], marker_color="#FFA15A"))
            fig.add_trace(go.Bar(name="ThruPlays", x=df_camp["Campanha"], y=df_camp["ThruPlays"], marker_color="#19D3F3"))
            fig.update_layout(barmode="group", height=350, xaxis_tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)

        if total_leads > 0:
            df_l = df_camp[df_camp["Leads"] > 0]
            col_e, col_f = st.columns(2)
            with col_e:
                fig = px.pie(df_l, values="Leads", names="Campanha", title="Distribuição de Leads")
                st.plotly_chart(fig, use_container_width=True)
            with col_f:
                fig = px.bar(df_l.sort_values("CPL"), x="Campanha", y="CPL",
                             color="CPL", color_continuous_scale="Reds", text_auto=".2f", title="CPL por Campanha")
                fig.update_layout(coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)

        if df_camp["Objetivo"].nunique() > 1:
            st.subheader("Gasto por Objetivo")
            df_obj = df_camp.groupby("Objetivo")["Gasto"].sum().reset_index()
            fig = px.pie(df_obj, values="Gasto", names="Objetivo", title="Distribuição de Gasto por Objetivo")
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("Tabela Completa — Campanhas")
        cols_show = ["Campanha", "Objetivo", "Gasto", "Alcance", "Impressões", "Cliques",
                     "CTR (%)", "CPC", "CPM", "Frequência", "Leads", "CPL", "Compras", "CPP Compra",
                     "Video Views", "ThruPlays", "Cliques Externos"]
        st.dataframe(
            df_camp[cols_show].style.format({
                "Gasto": "{:.2f}", "CPC": "{:.2f}", "CPM": "{:.2f}", "CPP": "{:.2f}",
                "CTR (%)": "{:.2f}", "Frequência": "{:.1f}", "CPL": "{:.2f}", "CPP Compra": "{:.2f}",
            }).background_gradient(subset=["Gasto"], cmap="Blues")
             .background_gradient(subset=["CTR (%)"], cmap="Greens"),
            use_container_width=True, height=400,
        )
        csv = df_camp.drop(columns=["Todas Ações"]).to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar Campanhas CSV", csv, "campanhas.csv", "text/csv")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CONJUNTOS DE ANÚNCIOS
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    try:
        df_adset = load_adsets(selected_id, date_preset)
    except Exception as e:
        st.error(f"Erro: {e}")
        st.stop()

    if df_adset.empty:
        st.warning("Nenhum conjunto no período.")
    else:
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Conjuntos", len(df_adset))
        k2.metric("Total Gasto", fmt(df_adset["Gasto"].sum(), currency))
        k3.metric("Total Leads", f"{int(df_adset['Leads'].sum()):,}")
        k4.metric("CTR Médio", f"{df_adset['CTR (%)'].mean():.2f}%")

        st.subheader("Top Conjuntos por Gasto")
        fig = px.bar(df_adset.sort_values("Gasto").head(20), x="Gasto", y="Conjunto",
                     orientation="h", color="Gasto", color_continuous_scale="Purples",
                     hover_data=["Campanha", "CTR (%)", "CPL"])
        fig.update_layout(coloraxis_showscale=False, height=500)
        st.plotly_chart(fig, use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.scatter(df_adset, x="Gasto", y="CTR (%)", size="Impressões",
                             color="CPM", hover_name="Conjunto",
                             title="Gasto vs CTR (tamanho = Impressões)")
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.scatter(df_adset, x="CPC", y="CTR (%)", size="Cliques",
                             color="Frequência", hover_name="Conjunto",
                             title="CPC vs CTR (tamanho = Cliques)")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Tabela Completa — Conjuntos")
        st.dataframe(
            df_adset.style.format({
                "Gasto": "{:.2f}", "CPC": "{:.2f}", "CPM": "{:.2f}",
                "CTR (%)": "{:.2f}", "Frequência": "{:.1f}", "CPL": "{:.2f}", "CPP": "{:.2f}",
            }).background_gradient(subset=["Gasto"], cmap="Purples"),
            use_container_width=True, height=420,
        )
        csv = df_adset.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar Conjuntos CSV", csv, "conjuntos.csv", "text/csv")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ANÚNCIOS
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    try:
        df_ads = load_ads(selected_id, date_preset)
    except Exception as e:
        st.error(f"Erro: {e}")
        st.stop()

    if df_ads.empty:
        st.warning("Nenhum anúncio no período.")
    else:
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Anúncios", len(df_ads))
        k2.metric("Total Gasto", fmt(df_ads["Gasto"].sum(), currency))
        k3.metric("Melhor CTR", f"{df_ads['CTR (%)'].max():.2f}%")
        k4.metric("Total Leads", f"{int(df_ads['Leads'].sum()):,}")

        st.subheader("Top 20 Anúncios por Gasto")
        fig = px.bar(df_ads.sort_values("Gasto").tail(20), x="Gasto", y="Anúncio",
                     orientation="h", color="CTR (%)", color_continuous_scale="RdYlGn",
                     hover_data=["Campanha", "Conjunto", "CPL"])
        fig.update_layout(height=550)
        st.plotly_chart(fig, use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.scatter(df_ads, x="Gasto", y="CTR (%)", size="Impressões",
                             color="CPC", hover_name="Anúncio",
                             title="Gasto vs CTR por Anúncio")
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            if df_ads["Video Views"].sum() > 0:
                fig = px.bar(df_ads[df_ads["Video Views"] > 0].sort_values("Video Views").tail(15),
                             x="Video Views", y="Anúncio", orientation="h",
                             color="ThruPlays", title="Video Views por Anúncio")
                st.plotly_chart(fig, use_container_width=True)

        st.subheader("Tabela Completa — Anúncios")
        st.dataframe(
            df_ads.style.format({
                "Gasto": "{:.2f}", "CPC": "{:.2f}", "CPM": "{:.2f}",
                "CTR (%)": "{:.2f}", "Frequência": "{:.1f}", "CPL": "{:.2f}", "CPP": "{:.2f}",
            }).background_gradient(subset=["Gasto"], cmap="Oranges")
             .background_gradient(subset=["CTR (%)"], cmap="Greens"),
            use_container_width=True, height=440,
        )
        csv = df_ads.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar Anúncios CSV", csv, "anuncios.csv", "text/csv")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — PÚBLICO
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    try:
        df_age, df_gender, df_ag = load_demographics(selected_id, date_preset)
    except Exception as e:
        st.error(f"Erro: {e}")
        st.stop()

    st.subheader("Por Faixa Etária")
    if not df_age.empty:
        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.bar(df_age, x="age", y="Impressões", color="Impressões",
                         color_continuous_scale="Blues", title="Impressões por Idade")
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.bar(df_age, x="age", y="Gasto", color="Gasto",
                         color_continuous_scale="Reds", title="Gasto por Idade")
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        col_c, col_d = st.columns(2)
        with col_c:
            fig = px.bar(df_age, x="age", y="CTR (%)", color="CTR (%)",
                         color_continuous_scale="Greens", title="CTR por Idade")
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        with col_d:
            if df_age["Leads"].sum() > 0:
                fig = px.bar(df_age[df_age["Leads"] > 0], x="age", y="Leads",
                             color="Leads", color_continuous_scale="Purples", title="Leads por Idade")
                fig.update_layout(coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df_age, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Por Gênero")
    if not df_gender.empty:
        gender_label = {"male": "Masculino", "female": "Feminino", "unknown": "Desconhecido"}
        df_gender["Gênero"] = df_gender["gender"].map(gender_label).fillna(df_gender["gender"])

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            fig = px.pie(df_gender, values="Impressões", names="Gênero", title="Impressões por Gênero")
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.pie(df_gender, values="Gasto", names="Gênero", title="Gasto por Gênero")
            st.plotly_chart(fig, use_container_width=True)
        with col_c:
            fig = px.bar(df_gender, x="Gênero", y="CTR (%)", color="Gênero", title="CTR por Gênero")
            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df_gender.drop(columns=["gender"]), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Mapa de Calor — Gasto por Idade × Gênero")
    if not df_ag.empty:
        gender_label = {"male": "Masculino", "female": "Feminino", "unknown": "Desconhecido"}
        df_ag["gender"] = df_ag["gender"].map(gender_label).fillna(df_ag["gender"])
        pivot = df_ag.pivot_table(index="age", columns="gender", values="Gasto", aggfunc="sum", fill_value=0)
        fig = px.imshow(pivot, text_auto=".1f", color_continuous_scale="RdYlGn",
                        title="Gasto por Faixa Etária × Gênero")
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 — POSICIONAMENTO
# ═══════════════════════════════════════════════════════════════════════════════
with tab6:
    try:
        df_place = load_placement(selected_id, date_preset)
    except Exception as e:
        st.error(f"Erro: {e}")
        st.stop()

    if df_place.empty:
        st.warning("Nenhum dado de posicionamento.")
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.pie(df_place, values="Gasto", names="Plataforma",
                         title="Distribuição de Gasto por Plataforma")
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.pie(df_place, values="Impressões", names="Plataforma",
                         title="Distribuição de Impressões por Plataforma")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("CTR por Posicionamento")
        fig = px.bar(df_place.sort_values("CTR (%)"), x="CTR (%)",
                     y=df_place["Plataforma"] + " / " + df_place["Posição"],
                     orientation="h", color="CTR (%)", color_continuous_scale="Greens",
                     text_auto=".2f")
        fig.update_layout(coloraxis_showscale=False, height=500)
        st.plotly_chart(fig, use_container_width=True)

        col_c, col_d = st.columns(2)
        with col_c:
            fig = px.bar(df_place, x="Plataforma", y="Gasto", color="Posição",
                         title="Gasto por Plataforma e Posição")
            st.plotly_chart(fig, use_container_width=True)
        with col_d:
            fig = px.bar(df_place, x="Plataforma", y="CPC", color="Posição",
                         barmode="group", title="CPC por Plataforma e Posição")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Tabela Completa — Posicionamento")
        st.dataframe(
            df_place.style.format({
                "Gasto": "{:.2f}", "CPC": "{:.2f}", "CPM": "{:.2f}", "CTR (%)": "{:.2f}",
            }).background_gradient(subset=["Gasto"], cmap="Blues"),
            use_container_width=True, hide_index=True,
        )
        csv = df_place.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar Posicionamento CSV", csv, "posicionamento.csv", "text/csv")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 7 — EVOLUÇÃO DIÁRIA
# ═══════════════════════════════════════════════════════════════════════════════
with tab7:
    try:
        df_daily = load_daily(selected_id, date_preset)
    except Exception as e:
        st.error(f"Erro: {e}")
        st.stop()

    if df_daily.empty:
        st.warning("Nenhum dado diário.")
    else:
        k1, k2, k3 = st.columns(3)
        k1.metric("Dias com gasto", int((df_daily["Gasto"] > 0).sum()))
        k2.metric("Pico de gasto diário", fmt(df_daily["Gasto"].max(), currency))
        k3.metric("Média diária", fmt(df_daily["Gasto"].mean(), currency))

        st.subheader("Gasto Diário")
        fig = px.area(df_daily, x="Data", y="Gasto", markers=True,
                      title="Evolução do Gasto Diário")
        fig.update_traces(fill="tozeroy", line_color="#636EFA")
        st.plotly_chart(fig, use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.line(df_daily, x="Data", y="CTR (%)", markers=True,
                          title="CTR Diário (%)")
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.line(df_daily, x="Data", y="CPM", markers=True,
                          title="CPM Diário")
            fig.update_traces(line_color="#EF553B")
            st.plotly_chart(fig, use_container_width=True)

        col_c, col_d = st.columns(2)
        with col_c:
            fig = px.bar(df_daily, x="Data", y="Impressões", title="Impressões Diárias")
            st.plotly_chart(fig, use_container_width=True)
        with col_d:
            fig = px.bar(df_daily, x="Data", y="Cliques", title="Cliques Diários",
                         color="Cliques", color_continuous_scale="Greens")
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        if df_daily["Leads"].sum() > 0:
            st.subheader("Leads Diários")
            fig = px.bar(df_daily, x="Data", y="Leads", title="Leads por Dia",
                         color="Leads", color_continuous_scale="Purples")
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Tabela Diária Completa")
        st.dataframe(
            df_daily.style.format({
                "Gasto": "{:.2f}", "CTR (%)": "{:.2f}", "CPM": "{:.2f}",
            }).background_gradient(subset=["Gasto"], cmap="Blues"),
            use_container_width=True, height=400,
        )
        csv = df_daily.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar Diário CSV", csv, "diario.csv", "text/csv")

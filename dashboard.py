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

def _get_token():
    try:
        token = st.secrets.get("FB_ACCESS_TOKEN")
        if token:
            return token
    except Exception:
        pass
    return os.getenv("FB_ACCESS_TOKEN")

ACCESS_TOKEN = _get_token()

st.set_page_config(page_title="316 — Meta Ads", page_icon="⚡", layout="wide")

# ── CSS moderno ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  /* Header */
  .dash-header {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 16px;
  }
  .dash-header h1 { color: #fff; font-size: 2rem; font-weight: 700; margin: 0; }
  .dash-header p  { color: #a0aec0; font-size: .9rem; margin: 4px 0 0; }

  /* KPI card */
  .kpi-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
    transition: transform .2s;
  }
  .kpi-card:hover { transform: translateY(-2px); }
  .kpi-card .label { color: #718096; font-size: .75rem; font-weight: 500; text-transform: uppercase; letter-spacing: .05em; }
  .kpi-card .value { color: #e2e8f0; font-size: 1.6rem; font-weight: 700; margin: 6px 0 2px; }
  .kpi-card .delta { color: #68d391; font-size: .8rem; }

  /* Insight cards */
  .insight-good  { background: linear-gradient(135deg,#1a3a2e,#1e4d3a); border-left: 4px solid #48bb78; border-radius: 10px; padding: 14px 18px; margin: 8px 0; }
  .insight-warn  { background: linear-gradient(135deg,#3a2e1a,#4d3e1e); border-left: 4px solid #ed8936; border-radius: 10px; padding: 14px 18px; margin: 8px 0; }
  .insight-bad   { background: linear-gradient(135deg,#3a1a1a,#4d1e1e); border-left: 4px solid #fc8181; border-radius: 10px; padding: 14px 18px; margin: 8px 0; }
  .insight-info  { background: linear-gradient(135deg,#1a2a3a,#1e3a4d); border-left: 4px solid #63b3ed; border-radius: 10px; padding: 14px 18px; margin: 8px 0; }
  .insight-good p, .insight-warn p, .insight-bad p, .insight-info p { color: #e2e8f0; margin: 0; font-size: .9rem; }
  .insight-good strong, .insight-warn strong, .insight-bad strong, .insight-info strong { font-size: 1rem; }

  /* Score */
  .score-circle { font-size: 3.5rem; font-weight: 800; text-align: center; padding: 16px; }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] { gap: 6px; }
  .stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0; padding: 10px 20px; font-weight: 500; }

  /* Ad Cards */
  .ad-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #2d3748;
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 14px;
    transition: transform .2s, border-color .2s;
    position: relative;
    overflow: hidden;
  }
  .ad-card:hover { transform: translateY(-3px); border-color: #4a5568; }
  .ad-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #636EFA, #EF553B);
  }
  .ad-card.green::before { background: linear-gradient(90deg, #48bb78, #38a169); }
  .ad-card.orange::before { background: linear-gradient(90deg, #ed8936, #dd6b20); }
  .ad-card.red::before { background: linear-gradient(90deg, #fc8181, #e53e3e); }
  .ad-card-title {
    color: #e2e8f0;
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 8px;
    line-height: 1.3;
  }
  .ad-breadcrumb {
    color: #718096;
    font-size: .75rem;
    margin-bottom: 12px;
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    align-items: center;
  }
  .ad-breadcrumb span { color: #4a5568; }
  .ad-metrics-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-top: 10px;
  }
  .ad-metric {
    background: rgba(255,255,255,0.04);
    border-radius: 8px;
    padding: 8px 10px;
    text-align: center;
  }
  .ad-metric .m-label { color: #718096; font-size: .65rem; text-transform: uppercase; letter-spacing: .06em; }
  .ad-metric .m-value { color: #e2e8f0; font-size: .95rem; font-weight: 700; margin-top: 2px; }
  .ad-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: .7rem;
    font-weight: 600;
    margin-bottom: 10px;
  }
  .badge-green { background: rgba(72,187,120,.2); color: #48bb78; }
  .badge-orange { background: rgba(237,137,54,.2); color: #ed8936; }
  .badge-red { background: rgba(252,129,129,.2); color: #fc8181; }

  /* Hierarchy */
  .hierarchy-camp {
    background: linear-gradient(135deg,#1a1a2e,#16213e);
    border: 1px solid #3d4f6b;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 12px;
  }
  .hierarchy-camp h4 { color: #90cdf4; margin: 0 0 4px; font-size: .95rem; }
  .hierarchy-adset {
    background: rgba(255,255,255,.04);
    border-left: 3px solid #4a5568;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    margin: 8px 0 8px 16px;
  }
  .hierarchy-adset h5 { color: #a0aec0; margin: 0 0 4px; font-size: .85rem; }

  /* Filter badge */
  .filter-bar {
    background: linear-gradient(135deg,#1a1a2e,#16213e);
    border: 1px solid #2d3748;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 18px;
  }
</style>
""", unsafe_allow_html=True)

# ── helpers ────────────────────────────────────────────────────────────────────
CHART_THEME = "plotly_dark"

def fmt(value, currency="BRL"):
    symbol = "R$" if currency == "BRL" else "$"
    try:
        return f"{symbol} {float(value):,.2f}"
    except Exception:
        return "–"

def safe_float(v, default=0.0):
    try: return float(v)
    except Exception: return default

def safe_int(v, default=0):
    try: return int(v)
    except Exception: return default

def extract_action(actions, action_type):
    if not actions: return 0
    for a in actions:
        if a.get("action_type") == action_type:
            return safe_int(a.get("value", 0))
    return 0

def extract_cpa(cpa_list, action_type):
    if not cpa_list: return 0.0
    for a in cpa_list:
        if a.get("action_type") == action_type:
            return safe_float(a.get("value", 0))
    return 0.0

def extract_all_actions(actions):
    if not actions: return {}
    return {a["action_type"]: safe_int(a.get("value", 0)) for a in actions}

def kpi(label, value, delta=None):
    delta_html = f'<div class="delta">▲ {delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="kpi-card">
      <div class="label">{label}</div>
      <div class="value">{value}</div>
      {delta_html}
    </div>""", unsafe_allow_html=True)

def insight(tipo, icon, title, text):
    cls = {"good": "insight-good", "warn": "insight-warn", "bad": "insight-bad", "info": "insight-info"}[tipo]
    st.markdown(f"""
    <div class="{cls}">
      <p><strong>{icon} {title}</strong></p>
      <p>{text}</p>
    </div>""", unsafe_allow_html=True)

STATUS_MAP = {1: "Ativa", 2: "Desativada", 3: "Suspensa", 7: "Pendente", 9: "Em revisão"}
PERIOD_LABELS = {
    "last_7d": "Últimos 7 dias", "last_14d": "Últimos 14 dias",
    "last_30d": "Últimos 30 dias", "last_90d": "Últimos 90 dias",
    "this_month": "Este mês", "last_month": "Mês passado",
}

# ── API calls ──────────────────────────────────────────────────────────────────
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

# ── header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
  <div>
    <h1>⚡ 316 — Meta Ads Intelligence</h1>
    <p>Dashboard completo com insights automáticos de performance</p>
  </div>
</div>
""", unsafe_allow_html=True)

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
    st.markdown("### ⚡ 316 Meta Ads")
    st.divider()
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
    st.divider()

    # Filtro de campanhas (carregado com spinner desativado para não duplicar)
    try:
        _df_camp_filter = load_campaigns(selected_id, date_preset)
        if not _df_camp_filter.empty:
            camp_names = sorted(_df_camp_filter["Campanha"].unique().tolist())
            selected_campaigns = st.multiselect(
                "🎯 Filtrar Campanhas",
                options=camp_names,
                default=[],
                placeholder="Todas as campanhas",
                help="Selecione campanhas específicas para filtrar os dados em todas as abas",
            )
        else:
            selected_campaigns = []
    except Exception:
        selected_campaigns = []

    st.divider()
    if st.button("🔄 Atualizar dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.caption("Dados atualizados a cada 5 minutos")

acc_info = account_map[selected_id]
currency = acc_info.get("currency", "BRL")

# ── tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab_ins = st.tabs([
    "🏦 Conta",
    "📣 Campanhas",
    "🗂️ Conjuntos",
    "🎨 Anúncios",
    "👥 Público",
    "📍 Posicionamento",
    "📅 Evolução Diária",
    "🧠 Insights",
])

def apply_camp_filter(df, col="Campanha"):
    """Aplica filtro de campanhas selecionadas na sidebar."""
    if selected_campaigns and col in df.columns:
        return df[df[col].isin(selected_campaigns)]
    return df

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — CONTA
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Informações da Conta")
    spent = safe_float(acc_info.get("amount_spent", 0)) / 100
    balance = safe_float(acc_info.get("balance", 0)) / 100
    spend_cap = safe_float(acc_info.get("spend_cap", 0)) / 100

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Nome", acc_info.get("name", "–"))
    with c2: kpi("Status", STATUS_MAP.get(acc_info.get("account_status"), "?"))
    with c3: kpi("Moeda", currency)
    with c4: kpi("Fuso Horário", acc_info.get("timezone_name", "–"))

    st.markdown("<br>", unsafe_allow_html=True)
    c5, c6, c7, c8 = st.columns(4)
    with c5: kpi("Total Gasto (histórico)", fmt(spent, currency))
    with c6: kpi("Saldo Disponível", fmt(balance, currency))
    with c7: kpi("Limite de Gasto", fmt(spend_cap, currency) if spend_cap else "Sem limite")
    with c8: kpi("Business", acc_info.get("business_name", "–"))

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
        st.error(f"Erro: {e}"); st.stop()

    df_camp = apply_camp_filter(df_camp)

    if selected_campaigns:
        st.info(f"🎯 Filtrando por: **{', '.join(selected_campaigns)}**")

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
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1: kpi("💰 Total Gasto", fmt(total_spend, currency))
        with c2: kpi("👥 Alcance", f"{int(total_reach):,}")
        with c3: kpi("👁️ Impressões", f"{int(total_imp):,}")
        with c4: kpi("🖱️ Cliques", f"{int(total_clicks):,}")
        with c5: kpi("📈 CTR Médio", f"{avg_ctr:.2f}%")
        with c6: kpi("📢 CPM Médio", fmt(avg_cpm, currency))

        st.markdown("<br>", unsafe_allow_html=True)
        c7, c8, c9, c10 = st.columns(4)
        with c7: kpi("🔁 Frequência Média", f"{avg_freq:.1f}x")
        with c8:
            if total_leads:
                kpi("🎯 Total Leads", f"{int(total_leads):,}")
            elif total_purchases:
                kpi("🛒 Total Compras", f"{int(total_purchases):,}")
        with c9:
            if total_leads:
                kpi("🎯 CPL Médio", fmt(total_spend / total_leads, currency))
            elif total_purchases:
                kpi("🛒 CPP Médio", fmt(total_spend / total_purchases, currency))
        with c10: kpi("📊 Campanhas Ativas", str(len(df_camp)))

        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.bar(df_camp.sort_values("Gasto"), x="Gasto", y="Campanha",
                         orientation="h", color="Gasto",
                         color_continuous_scale="Blues", text_auto=".2f",
                         title="Gasto por Campanha", template=CHART_THEME)
            fig.update_layout(coloraxis_showscale=False, height=420)
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.bar(df_camp.sort_values("CTR (%)"), x="CTR (%)", y="Campanha",
                         orientation="h", color="CTR (%)",
                         color_continuous_scale="Greens", text_auto=".2f",
                         title="CTR por Campanha", template=CHART_THEME)
            fig.update_layout(coloraxis_showscale=False, height=420)
            st.plotly_chart(fig, use_container_width=True)

        col_c, col_d = st.columns(2)
        with col_c:
            fig = go.Figure(layout=dict(template=CHART_THEME))
            fig.add_trace(go.Bar(name="Alcance", x=df_camp["Campanha"], y=df_camp["Alcance"], marker_color="#636EFA"))
            fig.add_trace(go.Bar(name="Impressões", x=df_camp["Campanha"], y=df_camp["Impressões"], marker_color="#EF553B"))
            fig.update_layout(barmode="group", height=380, xaxis_tickangle=-30, title="Alcance vs Impressões")
            st.plotly_chart(fig, use_container_width=True)
        with col_d:
            fig = go.Figure(layout=dict(template=CHART_THEME))
            fig.add_trace(go.Bar(name="CPC", x=df_camp["Campanha"], y=df_camp["CPC"], marker_color="#00CC96"))
            fig.add_trace(go.Bar(name="CPM", x=df_camp["Campanha"], y=df_camp["CPM"], marker_color="#AB63FA"))
            fig.update_layout(barmode="group", height=380, xaxis_tickangle=-30, title="CPC vs CPM")
            st.plotly_chart(fig, use_container_width=True)

        if df_camp["Video Views"].sum() > 0:
            fig = go.Figure(layout=dict(template=CHART_THEME))
            fig.add_trace(go.Bar(name="Video Views", x=df_camp["Campanha"], y=df_camp["Video Views"], marker_color="#FFA15A"))
            fig.add_trace(go.Bar(name="ThruPlays", x=df_camp["Campanha"], y=df_camp["ThruPlays"], marker_color="#19D3F3"))
            fig.update_layout(barmode="group", height=350, xaxis_tickangle=-30, title="Video Views vs ThruPlays")
            st.plotly_chart(fig, use_container_width=True)

        if total_leads > 0:
            df_l = df_camp[df_camp["Leads"] > 0]
            col_e, col_f = st.columns(2)
            with col_e:
                fig = px.pie(df_l, values="Leads", names="Campanha",
                             title="Distribuição de Leads", template=CHART_THEME, hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
            with col_f:
                fig = px.bar(df_l.sort_values("CPL"), x="Campanha", y="CPL",
                             color="CPL", color_continuous_scale="Reds",
                             text_auto=".2f", title="CPL por Campanha", template=CHART_THEME)
                fig.update_layout(coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)

        if df_camp["Objetivo"].nunique() > 1:
            df_obj = df_camp.groupby("Objetivo")["Gasto"].sum().reset_index()
            fig = px.pie(df_obj, values="Gasto", names="Objetivo",
                         title="Gasto por Objetivo", template=CHART_THEME, hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("Tabela Completa — Campanhas")
        cols_show = ["Campanha", "Objetivo", "Gasto", "Alcance", "Impressões", "Cliques",
                     "CTR (%)", "CPC", "CPM", "Frequência", "Leads", "CPL", "Compras", "CPP Compra",
                     "Video Views", "ThruPlays"]
        st.dataframe(
            df_camp[cols_show].style.format({
                "Gasto": "{:.2f}", "CPC": "{:.2f}", "CPM": "{:.2f}",
                "CTR (%)": "{:.2f}", "Frequência": "{:.1f}", "CPL": "{:.2f}", "CPP Compra": "{:.2f}",
            }).background_gradient(subset=["Gasto"], cmap="Blues")
             .background_gradient(subset=["CTR (%)"], cmap="Greens"),
            use_container_width=True, height=400,
        )
        csv = df_camp.drop(columns=["Todas Ações"]).to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar Campanhas CSV", csv, "campanhas.csv", "text/csv")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CONJUNTOS
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    try:
        df_adset = load_adsets(selected_id, date_preset)
    except Exception as e:
        st.error(f"Erro: {e}"); st.stop()

    df_adset = apply_camp_filter(df_adset)

    if selected_campaigns:
        st.info(f"🎯 Filtrando por campanhas: **{', '.join(selected_campaigns)}**")

    if df_adset.empty:
        st.warning("Nenhum conjunto no período.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1: kpi("Total Conjuntos", str(len(df_adset)))
        with c2: kpi("Total Gasto", fmt(df_adset["Gasto"].sum(), currency))
        with c3: kpi("Total Leads", f"{int(df_adset['Leads'].sum()):,}")
        with c4: kpi("CTR Médio", f"{df_adset['CTR (%)'].mean():.2f}%")

        st.markdown("<br>", unsafe_allow_html=True)
        fig = px.bar(df_adset.sort_values("Gasto").head(20), x="Gasto", y="Conjunto",
                     orientation="h", color="Gasto", color_continuous_scale="Purples",
                     hover_data=["Campanha", "CTR (%)", "CPL"],
                     title="Top 20 Conjuntos por Gasto", template=CHART_THEME)
        fig.update_layout(coloraxis_showscale=False, height=500)
        st.plotly_chart(fig, use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.scatter(df_adset, x="Gasto", y="CTR (%)", size="Impressões",
                             color="CPM", hover_name="Conjunto",
                             title="Gasto vs CTR (tamanho = Impressões)",
                             template=CHART_THEME)
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.scatter(df_adset, x="CPC", y="CTR (%)", size="Cliques",
                             color="Frequência", hover_name="Conjunto",
                             title="CPC vs CTR (tamanho = Cliques)",
                             template=CHART_THEME)
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
# TAB 4 — ANÚNCIOS (redesenhado)
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    try:
        df_ads = load_ads(selected_id, date_preset)
    except Exception as e:
        st.error(f"Erro: {e}"); st.stop()

    df_ads = apply_camp_filter(df_ads)

    if df_ads.empty:
        st.warning("Nenhum anúncio no período.")
    else:
        # ── Filtros inline ──────────────────────────────────────────────────
        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
        fcol1, fcol2 = st.columns(2)
        with fcol1:
            camp_opts = sorted(df_ads["Campanha"].unique().tolist())
            sel_camp_ad = st.multiselect(
                "📣 Campanha", camp_opts, key="ads_camp",
                placeholder="Todas as campanhas",
            )
        with fcol2:
            adset_opts_base = df_ads[df_ads["Campanha"].isin(sel_camp_ad)]["Conjunto"].unique() if sel_camp_ad else df_ads["Conjunto"].unique()
            sel_adset_ad = st.multiselect(
                "🗂️ Conjunto de Anúncios", sorted(adset_opts_base.tolist()), key="ads_adset",
                placeholder="Todos os conjuntos",
            )
        st.markdown('</div>', unsafe_allow_html=True)

        df_filtered = df_ads.copy()
        if sel_camp_ad:
            df_filtered = df_filtered[df_filtered["Campanha"].isin(sel_camp_ad)]
        if sel_adset_ad:
            df_filtered = df_filtered[df_filtered["Conjunto"].isin(sel_adset_ad)]

        # ── KPIs ────────────────────────────────────────────────────────────
        total_ads_spend = df_filtered["Gasto"].sum()
        total_ads_leads = df_filtered["Leads"].sum()
        best_ctr_ad = df_filtered["CTR (%)"].max() if len(df_filtered) > 0 else 0
        avg_cpc_ad = df_filtered["CPC"].mean() if len(df_filtered) > 0 else 0

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: kpi("🎨 Anúncios", str(len(df_filtered)))
        with c2: kpi("💰 Total Gasto", fmt(total_ads_spend, currency))
        with c3: kpi("📈 Melhor CTR", f"{best_ctr_ad:.2f}%")
        with c4: kpi("🖱️ CPC Médio", fmt(avg_cpc_ad, currency))
        with c5: kpi("🎯 Total Leads", f"{int(total_ads_leads):,}")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Modo de visualização ────────────────────────────────────────────
        view_mode = st.radio(
            "Visualização",
            ["📊 Gráficos", "🃏 Cards", "🌳 Hierarquia", "📋 Tabela"],
            horizontal=True,
            label_visibility="collapsed",
        )
        st.markdown("---")

        # ── GRÁFICOS ────────────────────────────────────────────────────────
        if view_mode == "📊 Gráficos":
            top20 = df_filtered.sort_values("Gasto").tail(20)
            fig = px.bar(top20, x="Gasto", y="Anúncio",
                         orientation="h", color="CTR (%)", color_continuous_scale="RdYlGn",
                         hover_data=["Campanha", "Conjunto", "CPL"],
                         title="Top 20 Anúncios por Gasto (cor = CTR)", template=CHART_THEME)
            fig.update_layout(height=max(400, len(top20) * 28), yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

            col_a, col_b = st.columns(2)
            with col_a:
                fig = px.scatter(df_filtered, x="Gasto", y="CTR (%)", size="Impressões",
                                 color="CPC", hover_name="Anúncio",
                                 hover_data=["Campanha", "Conjunto"],
                                 title="Gasto vs CTR (tamanho = Impressões)", template=CHART_THEME)
                st.plotly_chart(fig, use_container_width=True)
            with col_b:
                fig = px.scatter(df_filtered, x="CPM", y="CTR (%)", size="Cliques",
                                 color="Frequência", hover_name="Anúncio",
                                 hover_data=["Campanha", "Conjunto"],
                                 title="CPM vs CTR (tamanho = Cliques)", template=CHART_THEME)
                st.plotly_chart(fig, use_container_width=True)

            if df_filtered["Video Views"].sum() > 0:
                df_vid = df_filtered[df_filtered["Video Views"] > 0].sort_values("Video Views").tail(15)
                col_v1, col_v2 = st.columns(2)
                with col_v1:
                    fig = px.bar(df_vid, x="Video Views", y="Anúncio", orientation="h",
                                 color="Video Views", color_continuous_scale="Oranges",
                                 title="Video Views por Anúncio", template=CHART_THEME)
                    fig.update_layout(coloraxis_showscale=False)
                    st.plotly_chart(fig, use_container_width=True)
                with col_v2:
                    fig = px.bar(df_vid, x="ThruPlays", y="Anúncio", orientation="h",
                                 color="ThruPlays", color_continuous_scale="Teals",
                                 title="ThruPlays por Anúncio", template=CHART_THEME)
                    fig.update_layout(coloraxis_showscale=False)
                    st.plotly_chart(fig, use_container_width=True)

            if df_filtered["Leads"].sum() > 0:
                df_leads_ad = df_filtered[df_filtered["Leads"] > 0].sort_values("CPL")
                fig = px.bar(df_leads_ad.head(15), x="Anúncio", y="CPL",
                             color="Leads", color_continuous_scale="Purples",
                             title="CPL por Anúncio (top 15)", template=CHART_THEME)
                fig.update_layout(xaxis_tickangle=-30)
                st.plotly_chart(fig, use_container_width=True)

        # ── CARDS ───────────────────────────────────────────────────────────
        elif view_mode == "🃏 Cards":
            sort_by = st.selectbox(
                "Ordenar por",
                ["Gasto", "CTR (%)", "Leads", "Impressões", "CPC"],
                key="cards_sort",
            )
            df_cards = df_filtered.sort_values(sort_by, ascending=False)
            n_cols = 3
            cols_cards = st.columns(n_cols)

            for i, (_, ad) in enumerate(df_cards.iterrows()):
                ctr = ad["CTR (%)"]
                if ctr >= 2.0:
                    card_cls = "green"; badge_cls = "badge-green"; badge_txt = "✅ CTR Excelente"
                elif ctr >= 1.0:
                    card_cls = ""; badge_cls = "badge-orange"; badge_txt = "📈 CTR Bom"
                else:
                    card_cls = "red"; badge_cls = "badge-red"; badge_txt = "⚠️ CTR Baixo"

                name_short = (ad["Anúncio"][:50] + "…") if len(str(ad["Anúncio"])) > 50 else ad["Anúncio"]
                camp_short = (ad["Campanha"][:35] + "…") if len(str(ad["Campanha"])) > 35 else ad["Campanha"]
                conj_short = (ad["Conjunto"][:35] + "…") if len(str(ad["Conjunto"])) > 35 else ad["Conjunto"]
                leads_txt = f"{int(ad['Leads'])}" if ad["Leads"] > 0 else "–"
                cpl_txt = fmt(ad["CPL"], currency) if ad["CPL"] > 0 else "–"

                with cols_cards[i % n_cols]:
                    st.markdown(f"""
<div class="ad-card {card_cls}">
  <div class="ad-badge {badge_cls}">{badge_txt}</div>
  <div class="ad-card-title">{name_short}</div>
  <div class="ad-breadcrumb">
    📣 {camp_short}<span>›</span>🗂️ {conj_short}
  </div>
  <div class="ad-metrics-grid">
    <div class="ad-metric">
      <div class="m-label">💰 Gasto</div>
      <div class="m-value">{fmt(ad['Gasto'], currency)}</div>
    </div>
    <div class="ad-metric">
      <div class="m-label">📈 CTR</div>
      <div class="m-value">{ctr:.2f}%</div>
    </div>
    <div class="ad-metric">
      <div class="m-label">👁️ Impressões</div>
      <div class="m-value">{int(ad['Impressões']):,}</div>
    </div>
    <div class="ad-metric">
      <div class="m-label">🖱️ CPC</div>
      <div class="m-value">{fmt(ad['CPC'], currency)}</div>
    </div>
    <div class="ad-metric">
      <div class="m-label">🎯 Leads</div>
      <div class="m-value">{leads_txt}</div>
    </div>
    <div class="ad-metric">
      <div class="m-label">💡 CPL</div>
      <div class="m-value">{cpl_txt}</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

        # ── HIERARQUIA ──────────────────────────────────────────────────────
        elif view_mode == "🌳 Hierarquia":
            st.markdown("**Campanha → Conjunto → Anúncio**")
            st.markdown("<br>", unsafe_allow_html=True)

            for camp_name, camp_group in df_filtered.groupby("Campanha", sort=False):
                camp_spend = camp_group["Gasto"].sum()
                camp_leads = int(camp_group["Leads"].sum())
                camp_ctr = (camp_group["Cliques"].sum() / camp_group["Impressões"].sum() * 100) if camp_group["Impressões"].sum() > 0 else 0

                with st.expander(
                    f"📣 **{camp_name}** — 💰 {fmt(camp_spend, currency)} | CTR {camp_ctr:.2f}% | 🎯 {camp_leads} leads | {len(camp_group)} anúncios"
                ):
                    for adset_name, adset_group in camp_group.groupby("Conjunto", sort=False):
                        adset_spend = adset_group["Gasto"].sum()
                        adset_leads = int(adset_group["Leads"].sum())

                        st.markdown(f"""
<div class="hierarchy-adset">
  <h5>🗂️ {adset_name} &nbsp;·&nbsp; {fmt(adset_spend, currency)} &nbsp;·&nbsp; {adset_leads} leads &nbsp;·&nbsp; {len(adset_group)} anúncios</h5>
</div>""", unsafe_allow_html=True)

                        df_hier_show = adset_group[["Anúncio", "Gasto", "Impressões", "Cliques",
                                                      "CTR (%)", "CPC", "CPM", "Frequência",
                                                      "Leads", "CPL", "Video Views"]].copy()
                        st.dataframe(
                            df_hier_show.style.format({
                                "Gasto": "{:.2f}", "CPC": "{:.2f}", "CPM": "{:.2f}",
                                "CTR (%)": "{:.2f}", "Frequência": "{:.1f}", "CPL": "{:.2f}",
                            }).background_gradient(subset=["CTR (%)"], cmap="RdYlGn"),
                            use_container_width=True,
                            hide_index=True,
                        )

        # ── TABELA ──────────────────────────────────────────────────────────
        else:
            cols_show_ads = ["Campanha", "Conjunto", "Anúncio", "Gasto", "Impressões",
                             "Alcance", "Cliques", "CTR (%)", "CPC", "CPM", "Frequência",
                             "Leads", "CPL", "Compras", "Video Views", "ThruPlays"]
            st.dataframe(
                df_filtered[cols_show_ads].style.format({
                    "Gasto": "{:.2f}", "CPC": "{:.2f}", "CPM": "{:.2f}",
                    "CTR (%)": "{:.2f}", "Frequência": "{:.1f}", "CPL": "{:.2f}", "CPP": "{:.2f}",
                }).background_gradient(subset=["Gasto"], cmap="Oranges")
                 .background_gradient(subset=["CTR (%)"], cmap="RdYlGn"),
                use_container_width=True, height=520,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            csv = df_filtered.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Exportar Anúncios CSV", csv, "anuncios.csv", "text/csv", use_container_width=True)
        with col_dl2:
            # Resumo por campanha
            df_camp_summary = df_filtered.groupby("Campanha").agg(
                Anuncios=("Anúncio", "count"),
                Gasto=("Gasto", "sum"),
                Leads=("Leads", "sum"),
                Impressoes=("Impressões", "sum"),
                Cliques=("Cliques", "sum"),
            ).reset_index()
            df_camp_summary["CTR (%)"] = (df_camp_summary["Cliques"] / df_camp_summary["Impressoes"] * 100).round(2)
            csv2 = df_camp_summary.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Resumo por Campanha CSV", csv2, "resumo_campanhas.csv", "text/csv", use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — PÚBLICO
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    try:
        df_age, df_gender, df_ag = load_demographics(selected_id, date_preset)
    except Exception as e:
        st.error(f"Erro: {e}"); st.stop()

    st.subheader("Por Faixa Etária")
    if not df_age.empty:
        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.bar(df_age, x="age", y="Impressões", color="Impressões",
                         color_continuous_scale="Blues",
                         title="Impressões por Idade", template=CHART_THEME)
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.bar(df_age, x="age", y="Gasto", color="Gasto",
                         color_continuous_scale="Reds",
                         title="Gasto por Idade", template=CHART_THEME)
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        col_c, col_d = st.columns(2)
        with col_c:
            fig = px.bar(df_age, x="age", y="CTR (%)", color="CTR (%)",
                         color_continuous_scale="Greens",
                         title="CTR por Idade", template=CHART_THEME)
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        with col_d:
            if df_age["Leads"].sum() > 0:
                fig = px.bar(df_age[df_age["Leads"] > 0], x="age", y="Leads",
                             color="Leads", color_continuous_scale="Purples",
                             title="Leads por Idade", template=CHART_THEME)
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
            fig = px.pie(df_gender, values="Impressões", names="Gênero",
                         title="Impressões", template=CHART_THEME, hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.pie(df_gender, values="Gasto", names="Gênero",
                         title="Gasto", template=CHART_THEME, hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        with col_c:
            fig = px.bar(df_gender, x="Gênero", y="CTR (%)", color="Gênero",
                         title="CTR por Gênero", template=CHART_THEME)
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_gender.drop(columns=["gender"]), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Mapa de Calor — Gasto por Idade × Gênero")
    if not df_ag.empty:
        gender_label = {"male": "Masculino", "female": "Feminino", "unknown": "Desconhecido"}
        df_ag["gender"] = df_ag["gender"].map(gender_label).fillna(df_ag["gender"])
        pivot = df_ag.pivot_table(index="age", columns="gender", values="Gasto", aggfunc="sum", fill_value=0)
        fig = px.imshow(pivot, text_auto=".1f", color_continuous_scale="RdYlGn",
                        title="Gasto por Faixa Etária × Gênero", template=CHART_THEME)
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 — POSICIONAMENTO
# ═══════════════════════════════════════════════════════════════════════════════
with tab6:
    try:
        df_place = load_placement(selected_id, date_preset)
    except Exception as e:
        st.error(f"Erro: {e}"); st.stop()

    if df_place.empty:
        st.warning("Nenhum dado de posicionamento.")
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.pie(df_place, values="Gasto", names="Plataforma",
                         title="Gasto por Plataforma", template=CHART_THEME, hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.pie(df_place, values="Impressões", names="Plataforma",
                         title="Impressões por Plataforma", template=CHART_THEME, hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

        fig = px.bar(df_place.sort_values("CTR (%)"), x="CTR (%)",
                     y=df_place["Plataforma"] + " / " + df_place["Posição"],
                     orientation="h", color="CTR (%)", color_continuous_scale="Greens",
                     text_auto=".2f", title="CTR por Posicionamento", template=CHART_THEME)
        fig.update_layout(coloraxis_showscale=False, height=500)
        st.plotly_chart(fig, use_container_width=True)

        col_c, col_d = st.columns(2)
        with col_c:
            fig = px.bar(df_place, x="Plataforma", y="Gasto", color="Posição",
                         title="Gasto por Plataforma e Posição", template=CHART_THEME)
            st.plotly_chart(fig, use_container_width=True)
        with col_d:
            fig = px.bar(df_place, x="Plataforma", y="CPC", color="Posição",
                         barmode="group", title="CPC por Plataforma e Posição", template=CHART_THEME)
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
        st.error(f"Erro: {e}"); st.stop()

    if df_daily.empty:
        st.warning("Nenhum dado diário.")
    else:
        c1, c2, c3 = st.columns(3)
        with c1: kpi("Dias com gasto", str(int((df_daily["Gasto"] > 0).sum())))
        with c2: kpi("Pico de gasto diário", fmt(df_daily["Gasto"].max(), currency))
        with c3: kpi("Média diária", fmt(df_daily["Gasto"].mean(), currency))

        st.markdown("<br>", unsafe_allow_html=True)
        fig = px.area(df_daily, x="Data", y="Gasto", markers=True,
                      title="Evolução do Gasto Diário", template=CHART_THEME)
        fig.update_traces(fill="tozeroy", line_color="#636EFA", fillcolor="rgba(99,110,250,0.15)")
        st.plotly_chart(fig, use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.line(df_daily, x="Data", y="CTR (%)", markers=True,
                          title="CTR Diário (%)", template=CHART_THEME)
            fig.update_traces(line_color="#48bb78")
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.line(df_daily, x="Data", y="CPM", markers=True,
                          title="CPM Diário", template=CHART_THEME)
            fig.update_traces(line_color="#EF553B")
            st.plotly_chart(fig, use_container_width=True)

        col_c, col_d = st.columns(2)
        with col_c:
            fig = px.bar(df_daily, x="Data", y="Impressões",
                         title="Impressões Diárias", template=CHART_THEME,
                         color="Impressões", color_continuous_scale="Blues")
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        with col_d:
            fig = px.bar(df_daily, x="Data", y="Cliques",
                         title="Cliques Diários", template=CHART_THEME,
                         color="Cliques", color_continuous_scale="Greens")
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        if df_daily["Leads"].sum() > 0:
            fig = px.bar(df_daily, x="Data", y="Leads", title="Leads por Dia",
                         color="Leads", color_continuous_scale="Purples", template=CHART_THEME)
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

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 8 — INSIGHTS & RECOMENDAÇÕES
# ═══════════════════════════════════════════════════════════════════════════════
with tab_ins:
    st.markdown("## 🧠 Insights & Recomendações")
    st.caption(f"Análise automática baseada no período: **{PERIOD_LABELS[date_preset]}**")

    # Carrega dados necessários
    try:
        df_camp_i = load_campaigns(selected_id, date_preset)
        df_adset_i = load_adsets(selected_id, date_preset)
        df_ads_i = load_ads(selected_id, date_preset)
        df_daily_i = load_daily(selected_id, date_preset)
        try:
            df_age_i, df_gender_i, _ = load_demographics(selected_id, date_preset)
        except Exception:
            df_age_i, df_gender_i = pd.DataFrame(), pd.DataFrame()
        try:
            df_place_i = load_placement(selected_id, date_preset)
        except Exception:
            df_place_i = pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        st.stop()

    if df_camp_i.empty:
        st.warning("Sem dados suficientes para gerar insights no período selecionado.")
        st.stop()

    # ── Score de saúde ─────────────────────────────────────────────────────────
    score = 100
    problemas = []

    total_imp_i = df_camp_i["Impressões"].sum()
    total_clicks_i = df_camp_i["Cliques"].sum()
    total_spend_i = df_camp_i["Gasto"].sum()
    total_leads_i = df_camp_i["Leads"].sum()
    avg_ctr_i = (total_clicks_i / total_imp_i * 100) if total_imp_i else 0
    avg_freq_i = df_camp_i["Frequência"].mean()
    avg_cpm_i = (total_spend_i / total_imp_i * 1000) if total_imp_i else 0

    if avg_freq_i > 4: score -= 20; problemas.append("frequência muito alta")
    elif avg_freq_i > 3: score -= 10; problemas.append("frequência alta")

    if avg_ctr_i < 0.5: score -= 20; problemas.append("CTR muito baixo")
    elif avg_ctr_i < 1.0: score -= 10; problemas.append("CTR abaixo do ideal")

    if not df_daily_i.empty:
        gasto_std = df_daily_i["Gasto"].std()
        gasto_mean = df_daily_i["Gasto"].mean()
        if gasto_mean > 0 and (gasto_std / gasto_mean) > 0.5:
            score -= 10; problemas.append("gasto muito irregular")

    if len(df_camp_i) > 0:
        top_share = df_camp_i["Gasto"].max() / total_spend_i if total_spend_i else 0
        if top_share > 0.8: score -= 10; problemas.append("concentração de verba em 1 campanha")

    score = max(0, score)
    if score >= 80: score_color = "#48bb78"; score_label = "Saudável"
    elif score >= 60: score_color = "#ed8936"; score_label = "Atenção"
    else: score_color = "#fc8181"; score_label = "Crítico"

    col_score, col_prob = st.columns([1, 3])
    with col_score:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:16px;padding:32px;text-align:center;border:1px solid #2d3748">
          <div style="color:#718096;font-size:.85rem;text-transform:uppercase;letter-spacing:.1em">Score de Saúde</div>
          <div style="color:{score_color};font-size:4rem;font-weight:800;margin:8px 0">{score}</div>
          <div style="color:{score_color};font-size:1.1rem;font-weight:600">{score_label}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_prob:
        st.markdown("#### Pontos identificados:")
        if not problemas:
            st.success("Nenhum problema crítico detectado. Continue monitorando!")
        else:
            for p in problemas:
                st.warning(f"⚠️ {p.capitalize()}")

    st.divider()

    # ── Seções de insights ─────────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Performance Geral")

        # CTR
        if avg_ctr_i >= 2.0:
            insight("good", "✅", "CTR Excelente", f"CTR médio de <strong>{avg_ctr_i:.2f}%</strong> está acima da média do mercado (1–2%). Seus criativos estão performando muito bem.")
        elif avg_ctr_i >= 1.0:
            insight("info", "📈", "CTR Dentro do Esperado", f"CTR médio de <strong>{avg_ctr_i:.2f}%</strong>. Há espaço para melhorar testando novos criativos e chamadas para ação.")
        elif avg_ctr_i >= 0.5:
            insight("warn", "⚠️", "CTR Abaixo do Ideal", f"CTR médio de <strong>{avg_ctr_i:.2f}%</strong>. Considere renovar os criativos ou rever a segmentação de público.")
        else:
            insight("bad", "🚨", "CTR Muito Baixo", f"CTR de <strong>{avg_ctr_i:.2f}%</strong> está muito abaixo do esperado. Revise urgentemente criativos, copy e segmentação.")

        # Frequência
        if avg_freq_i > 4:
            insight("bad", "🚨", "Fadiga de Público Severa", f"Frequência média de <strong>{avg_freq_i:.1f}x</strong>. O público já viu seus anúncios muitas vezes — aumente o público-alvo ou renove os criativos imediatamente.")
        elif avg_freq_i > 3:
            insight("warn", "⚠️", "Atenção: Frequência Alta", f"Frequência média de <strong>{avg_freq_i:.1f}x</strong>. Risco de fadiga de público. Considere expandir o público ou trocar criativos.")
        elif avg_freq_i >= 1.5:
            insight("good", "✅", "Frequência Ideal", f"Frequência média de <strong>{avg_freq_i:.1f}x</strong> está dentro da faixa recomendada (1.5–3x).")
        else:
            insight("info", "📋", "Frequência Baixa", f"Frequência de <strong>{avg_freq_i:.1f}x</strong>. Pode indicar público muito amplo ou orçamento insuficiente para saturar o público.")

        # CPM
        insight("info", "💡", "CPM Médio da Conta",
                f"Seu CPM médio é <strong>{fmt(avg_cpm_i, currency)}</strong>. CPMs altos indicam leilões competitivos — tente segmentações mais específicas ou horários alternativos.")

    with col2:
        st.markdown("### 🎯 Campanhas")

        # Melhor e pior campanha
        if len(df_camp_i) > 0:
            best = df_camp_i.loc[df_camp_i["CTR (%)"].idxmax()]
            worst = df_camp_i.loc[df_camp_i["CTR (%)"].idxmin()]
            insight("good", "🏆", "Melhor Campanha por CTR",
                    f"<strong>{best['Campanha']}</strong> com CTR de {best['CTR (%)']:.2f}% e gasto de {fmt(best['Gasto'], currency)}. Use como referência para otimizar as demais.")
            if len(df_camp_i) > 1:
                insight("warn", "🔻", "Campanha com Menor CTR",
                        f"<strong>{worst['Campanha']}</strong> com CTR de {worst['CTR (%)']:.2f}%. Avalie pausar ou reformular esta campanha.")

        # Concentração de orçamento
        if len(df_camp_i) > 1 and total_spend_i > 0:
            top_camp = df_camp_i.nlargest(1, "Gasto").iloc[0]
            share = top_camp["Gasto"] / total_spend_i * 100
            if share > 70:
                insight("warn", "⚠️", "Concentração de Verba",
                        f"<strong>{share:.0f}%</strong> do orçamento está em uma única campanha (<em>{top_camp['Campanha']}</em>). Diversifique para reduzir risco.")
            else:
                insight("good", "✅", "Distribuição de Orçamento Saudável",
                        f"Nenhuma campanha concentra mais de <strong>{share:.0f}%</strong> do orçamento. Boa diversificação de risco.")

        # Leads / conversões
        if total_leads_i > 0 and total_spend_i > 0:
            cpl_medio = total_spend_i / total_leads_i
            insight("info", "🎯", f"CPL Médio: {fmt(cpl_medio, currency)}",
                    f"Total de <strong>{int(total_leads_i)}</strong> leads gerados. Compare com o valor do cliente para avaliar ROI.")
            # CPL por campanha
            df_leads_camp = df_camp_i[df_camp_i["Leads"] > 0].copy()
            if len(df_leads_camp) > 1:
                best_cpl = df_leads_camp.loc[df_leads_camp["CPL"].replace(0, float("inf")).idxmin()]
                insight("good", "🥇", "Campanha com Menor CPL",
                        f"<strong>{best_cpl['Campanha']}</strong> com CPL de {fmt(best_cpl['CPL'], currency)}. Considere aumentar o orçamento desta campanha.")

    st.divider()
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### 👥 Público")

        if not df_age_i.empty:
            best_age = df_age_i.loc[df_age_i["CTR (%)"].idxmax()]
            worst_age = df_age_i.loc[df_age_i["Gasto"].idxmax()]
            insight("good", "🎯", f"Melhor Faixa Etária por CTR: {best_age['age']}",
                    f"CTR de <strong>{best_age['CTR (%)']:.2f}%</strong>. Considere criar campanhas específicas para este público.")
            insight("info", "💰", f"Faixa que mais consome orçamento: {worst_age['age']}",
                    f"Gasto de <strong>{fmt(worst_age['Gasto'], currency)}</strong>. Verifique se o ROI justifica este investimento.")

            if df_age_i["Leads"].sum() > 0:
                best_age_leads = df_age_i.loc[df_age_i["Leads"].idxmax()]
                insight("good", "🏆", f"Faixa que mais gera leads: {best_age_leads['age']}",
                        f"<strong>{int(best_age_leads['Leads'])}</strong> leads. Priorize este público nas próximas campanhas.")

        if not df_gender_i.empty and len(df_gender_i) > 1:
            gender_label_map = {"male": "Masculino", "female": "Feminino", "unknown": "Desconhecido"}
            df_gender_i["Gênero"] = df_gender_i["gender"].map(gender_label_map).fillna(df_gender_i["gender"])
            best_g = df_gender_i.loc[df_gender_i["CTR (%)"].idxmax()]
            insight("info", "⚡", f"Melhor gênero por CTR: {best_g['Gênero']}",
                    f"CTR de <strong>{best_g['CTR (%)']:.2f}%</strong>. Avalie direcionar mais verba para este segmento.")

    with col4:
        st.markdown("### 📍 Posicionamento")

        if not df_place_i.empty:
            best_place = df_place_i.loc[df_place_i["CTR (%)"].idxmax()]
            worst_place = df_place_i.loc[df_place_i["CPC"].replace(0, float("inf")).idxmin()]
            insight("good", "🏆", f"Melhor posição por CTR",
                    f"<strong>{best_place['Plataforma']} / {best_place['Posição']}</strong> com CTR de {best_place['CTR (%)']:.2f}%. Priorize este posicionamento.")
            insight("good", "💸", f"Menor CPC por posição",
                    f"<strong>{worst_place['Plataforma']} / {worst_place['Posição']}</strong> com CPC de {fmt(worst_place['CPC'], currency)}. Ótimo custo por clique.")

            # Plataforma com mais gasto
            plat_gasto = df_place_i.groupby("Plataforma")["Gasto"].sum()
            top_plat = plat_gasto.idxmax()
            top_pct = plat_gasto[top_plat] / plat_gasto.sum() * 100
            insight("info", "📊", f"{top_pct:.0f}% do gasto em {top_plat.capitalize()}",
                    f"Verifique se a distribuição entre plataformas reflete o comportamento do seu público-alvo.")

    st.divider()
    st.markdown("### 📅 Tendências Temporais")

    if not df_daily_i.empty and len(df_daily_i) >= 7:
        col5, col6 = st.columns(2)
        mid = len(df_daily_i) // 2
        primeira = df_daily_i.iloc[:mid]
        segunda = df_daily_i.iloc[mid:]
        gasto_trend = segunda["Gasto"].mean() - primeira["Gasto"].mean()
        ctr_trend = segunda["CTR (%)"].mean() - primeira["CTR (%)"].mean()

        with col5:
            if gasto_trend > 0:
                insight("info", "📈", "Gasto em Alta",
                        f"O gasto médio diário aumentou <strong>{fmt(abs(gasto_trend), currency)}</strong> na segunda metade do período. Verifique se os resultados acompanham o aumento.")
            else:
                insight("warn", "📉", "Gasto em Queda",
                        f"O gasto médio diário caiu <strong>{fmt(abs(gasto_trend), currency)}</strong> na segunda metade do período. Verifique limites de campanha ou orçamentos esgotados.")

        with col6:
            if ctr_trend > 0.1:
                insight("good", "✅", "CTR em Melhora",
                        f"CTR médio subiu <strong>{ctr_trend:.2f}%</strong> na segunda metade do período. Boa tendência — continue com a estratégia atual.")
            elif ctr_trend < -0.1:
                insight("bad", "🚨", "CTR em Queda",
                        f"CTR médio caiu <strong>{abs(ctr_trend):.2f}%</strong> na segunda metade do período. Sinal de fadiga — renove criativos ou ajuste a segmentação.")
            else:
                insight("info", "➡️", "CTR Estável",
                        f"Variação de CTR de <strong>{ctr_trend:.2f}%</strong>. Performance consistente ao longo do período.")

        # Melhor dia
        best_day = df_daily_i.loc[df_daily_i["CTR (%)"].idxmax()]
        best_day_name = best_day["Data"].strftime("%A, %d/%m") if hasattr(best_day["Data"], "strftime") else str(best_day["Data"])
        insight("info", "📆", f"Melhor dia do período",
                f"<strong>{best_day_name}</strong> teve o maior CTR ({best_day['CTR (%)']:.2f}%) com gasto de {fmt(best_day['Gasto'], currency)}. Analise o que diferenciou esse dia.")

    st.divider()
    st.markdown("### 💡 Plano de Ação Prioritário")

    acoes = []
    if avg_freq_i > 3:
        acoes.append(("🔴 Alta Prioridade", "Renovar criativos ou ampliar público para reduzir frequência"))
    if avg_ctr_i < 1.0:
        acoes.append(("🔴 Alta Prioridade", "Testar novos criativos com chamadas para ação mais diretas"))
    if total_leads_i > 0:
        df_leads_c = df_camp_i[df_camp_i["Leads"] > 0]
        if len(df_leads_c) > 1:
            best_cpl_c = df_leads_c.loc[df_leads_c["CPL"].replace(0, float("inf")).idxmin()]
            acoes.append(("🟡 Média Prioridade", f"Aumentar orçamento da campanha '{best_cpl_c['Campanha']}' (menor CPL)"))
    if len(df_camp_i) > 1:
        worst_ctr_c = df_camp_i.loc[df_camp_i["CTR (%)"].idxmin()]
        acoes.append(("🟡 Média Prioridade", f"Pausar ou reformular '{worst_ctr_c['Campanha']}' (menor CTR: {worst_ctr_c['CTR (%)']:.2f}%)"))
    if not df_place_i.empty:
        best_pl = df_place_i.loc[df_place_i["CTR (%)"].idxmax()]
        acoes.append(("🟢 Oportunidade", f"Priorizar posicionamento {best_pl['Plataforma']}/{best_pl['Posição']} (CTR {best_pl['CTR (%)']:.2f}%)"))
    if not df_age_i.empty:
        best_ag = df_age_i.loc[df_age_i["CTR (%)"].idxmax()]
        acoes.append(("🟢 Oportunidade", f"Criar campanha específica para faixa {best_ag['age']} (CTR {best_ag['CTR (%)']:.2f}%)"))

    if acoes:
        for prioridade, acao in acoes:
            cor = "bad" if "Alta" in prioridade else "warn" if "Média" in prioridade else "good"
            insight(cor, "", prioridade, acao)
    else:
        insight("good", "✅", "Conta em bom estado", "Nenhuma ação crítica identificada. Continue monitorando e testando novos criativos regularmente.")

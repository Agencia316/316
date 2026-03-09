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

# set_page_config DEVE ser o primeiro comando Streamlit
st.set_page_config(page_title="316 — Meta Ads", page_icon="⚡", layout="wide")

def _get_token():
    try:
        token = st.secrets.get("FB_ACCESS_TOKEN")
        if token:
            return token
    except Exception:
        pass
    return os.getenv("FB_ACCESS_TOKEN")

ACCESS_TOKEN = _get_token()

# ── CSS ────────────────────────────────────────────────────────────────────────
st.html("""
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
/* ── BASE ── */
html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }
.stApp { background-color: #020617 !important; }
.block-container { padding-top: 16px !important; padding-bottom: 60px !important; }
h1,h2,h3,h4,h5,h6,p,span,div,label { color: #F8FAFC; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
  background: rgba(2,6,23,.98) !important;
  border-right: 1px solid rgba(255,255,255,.06) !important;
}
[data-testid="stSidebar"] * { color: #94A3B8 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #F8FAFC !important; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(255,255,255,.03) !important;
  border-radius: 12px !important;
  padding: 4px !important;
  border: 1px solid rgba(255,255,255,.05) !important;
  gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: #475569 !important;
  border-radius: 8px !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  padding: 8px 18px !important;
  border: none !important;
  transition: all .2s !important;
}
.stTabs [aria-selected="true"] {
  background: rgba(56,189,248,.12) !important;
  color: #38BDF8 !important;
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ── MISC ── */
hr { border-color: rgba(255,255,255,.06) !important; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,.1); border-radius: 4px; }
[data-testid="stDataFrame"] {
  border: 1px solid rgba(255,255,255,.07) !important;
  border-radius: 12px !important;
}

/* ── KPI CARD ── */
.kpi-card {
  background: rgba(255,255,255,.025);
  border: 1px solid rgba(255,255,255,.07);
  border-radius: 20px; padding: 22px 24px;
  position: relative; overflow: hidden;
  transition: transform .25s cubic-bezier(.2,0,0,1), box-shadow .25s;
  margin-bottom: 4px;
}
.kpi-card:hover { transform: translateY(-3px); border-color: rgba(255,255,255,.12); }
.kpi-top { position: absolute; top: 0; left: 0; right: 0; height: 2px; }
.kpi-glow { position: absolute; top:-40px; right:-40px; width:120px; height:120px; border-radius:50%; opacity:.05; filter:blur(30px); }
.kpi-row { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:14px; }
.kpi-label { font-size:10px; letter-spacing:3px; color:#475569; text-transform:uppercase; font-family:'JetBrains Mono',monospace; }
.kpi-icon-box { width:32px; height:32px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:16px; }
.kpi-value { font-size:28px; font-weight:800; color:#F8FAFC; font-family:'Outfit',sans-serif; line-height:1; margin-bottom:10px; }
.kpi-delta-row { display:flex; align-items:center; gap:8px; }
.kpi-badge { font-size:11px; padding:2px 8px; border-radius:20px; font-family:'JetBrains Mono',monospace; font-weight:600; }
.kpi-sub { font-size:11px; color:#475569; }

/* ── SECTION LABEL ── */
.slabel { display:flex; align-items:center; gap:10px; margin-bottom:20px; }
.slabel-bar { width:2px; height:18px; background:linear-gradient(180deg,#38BDF8,#818CF8); border-radius:4px; flex-shrink:0; }
.slabel-text { font-size:12px; font-weight:700; letter-spacing:3px; text-transform:uppercase; color:#94A3B8; font-family:'JetBrains Mono',monospace; margin:0; }

/* ── INSIGHTS ── */
.insight-good, .insight-warn, .insight-bad, .insight-info {
  border-radius: 12px; padding: 14px 18px; margin: 8px 0;
}
.insight-good { background:rgba(52,211,153,.06); border:1px solid rgba(52,211,153,.2); border-left:3px solid #34D399; }
.insight-warn { background:rgba(251,191,36,.06); border:1px solid rgba(251,191,36,.2); border-left:3px solid #FBBF24; }
.insight-bad  { background:rgba(248,113,113,.06); border:1px solid rgba(248,113,113,.2); border-left:3px solid #F87171; }
.insight-info { background:rgba(56,189,248,.06);  border:1px solid rgba(56,189,248,.2);  border-left:3px solid #38BDF8; }
.insight-good p, .insight-warn p, .insight-bad p, .insight-info p { color:#CBD5E1; margin:0; font-size:.88rem; }
.insight-good strong, .insight-warn strong, .insight-bad strong, .insight-info strong { color:#F8FAFC; }

/* ── AD CARDS ── */
.ad-card {
  background: rgba(255,255,255,.025);
  border: 1px solid rgba(255,255,255,.07);
  border-radius: 16px; padding: 18px 20px; margin-bottom: 14px;
  transition: transform .25s; position: relative; overflow: hidden;
}
.ad-card:hover { transform: translateY(-3px); }
.ad-card::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; background:linear-gradient(90deg,#38BDF8,#818CF8); }
.ad-card.green::before  { background:linear-gradient(90deg,#34D399,#10B981); }
.ad-card.orange::before { background:linear-gradient(90deg,#FBBF24,#F59E0B); }
.ad-card.red::before    { background:linear-gradient(90deg,#F87171,#EF4444); }
.ad-card-title { color:#E2E8F0; font-size:1rem; font-weight:600; margin-bottom:8px; }
.ad-breadcrumb { color:#475569; font-size:.75rem; margin-bottom:12px; }
.ad-metrics-grid { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:10px; }
.ad-metric { background:rgba(255,255,255,.04); border-radius:8px; padding:8px 10px; text-align:center; }
.ad-metric .m-label { color:#475569; font-size:.65rem; text-transform:uppercase; letter-spacing:.06em; font-family:'JetBrains Mono',monospace; }
.ad-metric .m-value { color:#E2E8F0; font-size:.95rem; font-weight:700; margin-top:2px; font-family:'JetBrains Mono',monospace; }
.ad-badge { display:inline-block; padding:2px 10px; border-radius:20px; font-size:.7rem; font-weight:600; margin-bottom:10px; font-family:'JetBrains Mono',monospace; }
.badge-green  { background:rgba(52,211,153,.15); color:#34D399; }
.badge-orange { background:rgba(251,191,36,.15);  color:#FBBF24; }
.badge-red    { background:rgba(248,113,113,.15); color:#F87171; }

/* ── HIERARCHY ── */
.hierarchy-adset {
  background:rgba(255,255,255,.03); border-left:2px solid rgba(56,189,248,.3);
  border-radius:0 10px 10px 0; padding:10px 14px; margin:8px 0 8px 16px;
}
.hierarchy-adset h5 { color:#94A3B8; margin:0 0 4px; font-size:.85rem; }

/* ── FILTER BAR ── */
.filter-bar {
  background:rgba(255,255,255,.025); border:1px solid rgba(255,255,255,.07);
  border-radius:14px; padding:16px 20px; margin-bottom:18px;
}

/* ── SCORE ── */
.score-wrap {
  background:rgba(255,255,255,.025); border:1px solid rgba(255,255,255,.07);
  border-radius:20px; padding:32px; text-align:center;
}

/* ── ANIMATIONS ── */
@keyframes pulse-ring { 0%{transform:scale(1);opacity:.6} 100%{transform:scale(1.5);opacity:0} }
@keyframes fadeUp { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:translateY(0)} }
</style>
""")

# ── helpers ────────────────────────────────────────────────────────────────────
CHART_THEME = "plotly" if st.session_state.get("theme", "dark") == "light" else "plotly_dark"

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

def dark_fig(fig):
    """Aplica estilo dark consistente em figuras plotly."""
    fig.update_layout(
        paper_bgcolor="rgba(255,255,255,0.02)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#94A3B8",
        title_font=dict(color="#E2E8F0", family="Outfit", size=14),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94A3B8")),
        margin=dict(l=0, r=10, t=44, b=10),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(0,0,0,0)", tickcolor="rgba(0,0,0,0)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(0,0,0,0)", tickcolor="rgba(0,0,0,0)")
    return fig

def light_fig(fig):
    """Aplica estilo light consistente em figuras plotly."""
    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FAFC",
        font_color="#334155",
        title_font=dict(color="#0F172A", family="Outfit", size=14),
        legend=dict(bgcolor="rgba(255,255,255,0.8)", font=dict(color="#334155")),
        margin=dict(l=0, r=10, t=44, b=10),
    )
    fig.update_xaxes(gridcolor="rgba(0,0,0,0.06)", linecolor="rgba(0,0,0,0.1)", tickcolor="rgba(0,0,0,0.1)")
    fig.update_yaxes(gridcolor="rgba(0,0,0,0.06)", linecolor="rgba(0,0,0,0.1)", tickcolor="rgba(0,0,0,0.1)")
    return fig

def apply_fig(fig):
    """Aplica o tema selecionado (dark ou light) na figura."""
    if st.session_state.get("theme", "dark") == "light":
        return light_fig(fig)
    return dark_fig(fig)

def kpi(label, value, delta=None, icon="", color="#818CF8"):
    icon_html = f'<div class="kpi-icon-box" style="background:{color}18">{icon}</div>' if icon else ""
    delta_html = ""
    if delta is not None:
        try:
            num = float(str(delta).replace(",", ".").replace("%", "").replace("R$", "").replace(" ", ""))
            pos = num >= 0
        except Exception:
            pos = True
        c = "#34D399" if pos else "#F87171"
        bg = "rgba(52,211,153,.1)" if pos else "rgba(248,113,113,.1)"
        arr = "↑" if pos else "↓"
        delta_html = f'<div class="kpi-delta-row"><span class="kpi-badge" style="color:{c};background:{bg}">{arr} {delta}</span></div>'
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-top" style="background:linear-gradient(90deg,{color},transparent)"></div>
      <div class="kpi-glow" style="background:{color}"></div>
      <div class="kpi-row">
        <span class="kpi-label">{label}</span>
        {icon_html}
      </div>
      <div class="kpi-value">{value}</div>
      {delta_html}
    </div>""", unsafe_allow_html=True)

def slabel(text):
    st.markdown(f"""<div class="slabel"><div class="slabel-bar"></div><p class="slabel-text">{text}</p></div>""",
                unsafe_allow_html=True)

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
        conversas = extract_action(actions, "onsite_conversion.messaging_conversation_started_7d")
        primeiras_resp = extract_action(actions, "onsite_conversion.messaging_first_reply")
        bloqueios = extract_action(actions, "onsite_conversion.messaging_block")
        conexoes_msg = extract_action(actions, "onsite_conversion.total_messaging_connection")
        custo_conversa = extract_cpa(cpa_list, "onsite_conversion.messaging_conversation_started_7d")
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
            "Conversas": conversas,
            "Custo/Conversa": custo_conversa,
            "Primeiras Respostas": primeiras_resp,
            "Bloqueios": bloqueios,
            "Conexões Msg": conexoes_msg,
            "Taxa Resposta (%)": round(primeiras_resp / conversas * 100, 1) if conversas > 0 else 0.0,
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
        conversas = extract_action(actions, "onsite_conversion.messaging_conversation_started_7d")
        primeiras_resp = extract_action(actions, "onsite_conversion.messaging_first_reply")
        bloqueios = extract_action(actions, "onsite_conversion.messaging_block")
        custo_conversa = extract_cpa(cpa_list, "onsite_conversion.messaging_conversation_started_7d")
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
            "Conversas": conversas,
            "Custo/Conversa": custo_conversa,
            "Primeiras Respostas": primeiras_resp,
            "Bloqueios": bloqueios,
            "Taxa Resposta (%)": round(primeiras_resp / conversas * 100, 1) if conversas > 0 else 0.0,
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
        conversas = extract_action(actions, "onsite_conversion.messaging_conversation_started_7d")
        primeiras_resp = extract_action(actions, "onsite_conversion.messaging_first_reply")
        bloqueios = extract_action(actions, "onsite_conversion.messaging_block")
        custo_conversa = extract_cpa(cpa_list, "onsite_conversion.messaging_conversation_started_7d")
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
            "Conversas": conversas,
            "Custo/Conversa": custo_conversa,
            "Primeiras Respostas": primeiras_resp,
            "Bloqueios": bloqueios,
            "Taxa Resposta (%)": round(primeiras_resp / conversas * 100, 1) if conversas > 0 else 0.0,
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

DEMO_MODE = False

if not ACCESS_TOKEN:
    DEMO_MODE = True
else:
    try:
        accounts = load_accounts()
    except Exception:
        DEMO_MODE = True

if DEMO_MODE:
    import random, datetime as _dt
    random.seed(42)
    _today = _dt.date.today()
    # Meta API retorna amount_spent/balance/spend_cap em centavos (divididos por 100 no Tab1)
    accounts = [{"id": "act_demo316", "name": "Agência 316 — Demo", "currency": "BRL",
                 "account_status": 1, "amount_spent": "1845000", "balance": "500000",
                 "spend_cap": "3000000", "timezone_name": "America/Sao_Paulo", "business_name": "316"}]

    def _demo_campaigns(account_id, date_preset):
        # (nome, obj, spend, imp, reach, clicks, ctr, cpc, cpm, freq, leads, cpl, purchases, cpp, vid, thru, conversas, custo_conv, prim_resp, bloqueios)
        camps = [
            ("Campanha | Leads | Imóveis Premium",  "LEAD_GENERATION", 6800, 320000, 290000, 4100, 3.9,  1.66, 21.25, 1.34, 312, 21.79,  0,      0,      18200, 4200,  0,   0,    0,   0),
            ("Campanha | Mensagens | WhatsApp",       "MESSAGES",        4500, 210000, 195000, 3800, 1.81, 1.18, 21.43, 1.42,   0,     0,  0,      0,          0,    0,  387, 11.63, 341,  8),
            ("Campanha | Tráfego | Blog 316",        "LINK_CLICKS",     3200, 195000, 180000, 6800, 3.49, 0.47, 16.41, 1.28,   0,     0,  0,      0,          0,    0,    0,     0,   0,  0),
            ("Campanha | Conversões | Landing Page", "CONVERSIONS",     4100, 240000, 215000, 3600, 1.5,  1.14, 17.08, 1.12,  89, 46.07, 23, 178.26,          0,    0,   62, 66.13,  48, 14),
            ("Campanha | Remarketing | Visitantes",  "CONVERSIONS",     2350,  98000,  92000, 1900, 1.94, 1.24, 23.98, 1.07,  45, 52.22, 12, 195.83,          0,    0,   78, 30.13,  65,  6),
            ("Campanha | Awareness | Branding 316",  "REACH",           2000, 410000, 398000, 2100, 0.51, 0.95,  4.88, 1.03,   0,     0,  0,      0,      32000,18000,    0,     0,   0,  0),
        ]
        rows = []
        for camp, obj, spend, imp, reach, clicks, ctr, cpc, cpm, freq, leads, cpl, purchases, cpp, vid, thru, conversas, custo_conv, prim_resp, bloqueios in camps:
            rows.append({
                "ID": f"camp_{camp[:6].replace(' ','_')}",
                "Campanha": camp, "Objetivo": obj,
                "Gasto": spend, "Impressões": imp, "Alcance": reach, "Cliques": clicks,
                "Cliques Únicos": int(clicks*0.85), "CTR (%)": ctr, "CTR Único (%)": round(ctr*0.85,2),
                "CPC": cpc, "CPM": cpm, "CPP": round(spend/reach*1000,2) if reach else 0,
                "Frequência": freq, "Cliques no Link": int(clicks*0.7), "Cliques Externos": int(clicks*0.6),
                "Leads": leads, "CPL": cpl, "Compras": purchases, "CPP Compra": cpp,
                "Video Views": vid, "ThruPlays": thru,
                "Conversas": conversas, "Custo/Conversa": custo_conv,
                "Primeiras Respostas": prim_resp, "Bloqueios": bloqueios,
                "Conexões Msg": int(conversas * 1.15) if conversas else 0,
                "Taxa Resposta (%)": round(prim_resp / conversas * 100, 1) if conversas > 0 else 0.0,
                "Todas Ações": f"leads:{leads}, purchases:{purchases}, conversas:{conversas}",
            })
        return pd.DataFrame(rows)

    def _demo_adsets(account_id, date_preset):
        # (nome, camp, spend, imp, reach, clicks, ctr, cpc, cpm, freq, leads, cpl, purchases, conversas, custo_conv, prim_resp, bloqueios)
        sets = [
            ("Conj | Imóveis | 30-45 anos",   "Campanha | Leads | Imóveis Premium",  3200, 155000, 142000, 1950, 1.26, 1.64, 20.65, 1.22, 148, 21.62,  0,   0,     0,   0,  0),
            ("Conj | Imóveis | 45-60 anos",   "Campanha | Leads | Imóveis Premium",  3600, 165000, 148000, 2150, 1.30, 1.67, 21.82, 1.46, 164, 21.95,  0,   0,     0,   0,  0),
            ("Conj | WhatsApp | 25-45 anos",  "Campanha | Mensagens | WhatsApp",     2400, 112000, 104000, 2050, 1.83, 1.17, 21.43, 1.38,   0,     0,  0, 214, 11.21, 189,  4),
            ("Conj | WhatsApp | 45-65 anos",  "Campanha | Mensagens | WhatsApp",     2100,  98000,  91000, 1750, 1.79, 1.20, 21.43, 1.46,   0,     0,  0, 173, 12.14, 152,  4),
            ("Conj | Blog | Mobile",          "Campanha | Tráfego | Blog 316",       1600,  98000,  90000, 3400, 3.47, 0.47, 16.33, 1.30,   0,     0,  0,   0,     0,   0,  0),
            ("Conj | Blog | Desktop",         "Campanha | Tráfego | Blog 316",       1600,  97000,  90000, 3400, 3.51, 0.47, 16.49, 1.26,   0,     0,  0,   0,     0,   0,  0),
            ("Conj | Conversão | Leads Quentes", "Campanha | Conversões | Landing Page", 4100, 240000, 215000, 3600, 1.5, 1.14, 17.08, 1.12, 89, 46.07, 23,  62, 66.13,  48, 14),
        ]
        rows = []
        for name, camp, spend, imp, reach, clicks, ctr, cpc, cpm, freq, leads, cpl, purchases, conversas, custo_conv, prim_resp, bloqueios in sets:
            rows.append({
                "ID": f"adset_{name[:6].replace(' ','_')}",
                "Conjunto": name, "Campanha": camp,
                "Gasto": spend, "Impressões": imp, "Alcance": reach, "Cliques": clicks,
                "CTR (%)": ctr, "CPC": cpc, "CPM": cpm, "Frequência": freq,
                "Leads": leads, "CPL": cpl, "Compras": purchases,
                "CPP": round(spend/purchases,2) if purchases else 0,
                "Conversas": conversas, "Custo/Conversa": custo_conv,
                "Primeiras Respostas": prim_resp, "Bloqueios": bloqueios,
                "Taxa Resposta (%)": round(prim_resp / conversas * 100, 1) if conversas > 0 else 0.0,
            })
        return pd.DataFrame(rows)

    def _demo_ads(account_id, date_preset):
        # (nome, adset, camp, spend, imp, reach, clicks, ctr, cpc, cpm, freq, leads, cpl, purchases, vid, thru, conversas, custo_conv, prim_resp, bloqueios)
        ads = [
            ("Anúncio | Vídeo 15s | Imóveis",     "Conj | Imóveis | 30-45 anos",  "Campanha | Leads | Imóveis Premium", 1800, 85000, 78000, 1050, 1.24, 1.71, 21.18, 1.21, 78, 23.08, 0, 12000, 5000,   0,     0,   0,  0),
            ("Anúncio | Carrossel | Depoimentos",  "Conj | Imóveis | 30-45 anos",  "Campanha | Leads | Imóveis Premium", 1400, 70000, 64000,  900, 1.29, 1.56, 20.00, 1.23, 70, 20.00, 0,     0,    0,   0,     0,   0,  0),
            ("Anúncio | Imagem | CTA Forte",       "Conj | Imóveis | 45-60 anos",  "Campanha | Leads | Imóveis Premium", 1900, 88000, 80000, 1200, 1.36, 1.58, 21.59, 1.48, 90, 21.11, 0,     0,    0,   0,     0,   0,  0),
            ("Anúncio | Vídeo 30s | Branding",     "Conj | Imóveis | 45-60 anos",  "Campanha | Leads | Imóveis Premium", 1700, 77000, 68000,  950, 1.23, 1.79, 22.08, 1.44, 74, 22.97, 0,  8200, 3000,   0,     0,   0,  0),
            ("Anúncio | WhatsApp | Vídeo Curto",   "Conj | WhatsApp | 25-45 anos", "Campanha | Mensagens | WhatsApp",    1350, 63000, 58000, 1200, 1.90, 1.13, 21.43, 1.35,  0,     0, 0,     0,    0, 130, 10.38, 116,  2),
            ("Anúncio | WhatsApp | Carrossel",     "Conj | WhatsApp | 25-45 anos", "Campanha | Mensagens | WhatsApp",    1050, 49000, 46000, 850,  1.73, 1.24, 21.43, 1.41,  0,     0, 0,     0,    0,  84, 12.50,  73,  2),
            ("Anúncio | WhatsApp | Imagem | Oferta","Conj | WhatsApp | 45-65 anos","Campanha | Mensagens | WhatsApp",    2100, 98000, 91000, 1750, 1.79, 1.20, 21.43, 1.46,  0,     0, 0,     0,    0, 173, 12.14, 152,  4),
            ("Anúncio | Blog | Mobile Feed",       "Conj | Blog | Mobile",         "Campanha | Tráfego | Blog 316",      1600, 98000, 90000, 3400, 3.47, 0.47, 16.33, 1.30,  0,     0, 0,     0,    0,   0,     0,   0,  0),
        ]
        rows = []
        for name, adset, camp, spend, imp, reach, clicks, ctr, cpc, cpm, freq, leads, cpl, purchases, vid, thru, conversas, custo_conv, prim_resp, bloqueios in ads:
            rows.append({
                "ID": f"ad_{name[:6].replace(' ','_')}",
                "Anúncio": name, "Conjunto": adset, "Campanha": camp,
                "Gasto": spend, "Impressões": imp, "Alcance": reach, "Cliques": clicks,
                "Cliques Únicos": int(clicks*0.85), "CTR (%)": ctr, "CPC": cpc, "CPM": cpm, "Frequência": freq,
                "Leads": leads, "CPL": cpl, "Compras": purchases,
                "CPP": round(spend/purchases,2) if purchases else 0,
                "Video Views": vid, "ThruPlays": thru,
                "Conversas": conversas, "Custo/Conversa": custo_conv,
                "Primeiras Respostas": prim_resp, "Bloqueios": bloqueios,
                "Taxa Resposta (%)": round(prim_resp / conversas * 100, 1) if conversas > 0 else 0.0,
            })
        return pd.DataFrame(rows)

    def _demo_demographics(account_id, date_preset):
        age_data = [
            {"age": "18-24", "Impressões": 58000, "Alcance": 52000, "Cliques": 980, "Gasto": 1200.0, "CTR (%)": 1.69, "Leads": 28},
            {"age": "25-34", "Impressões": 145000, "Alcance": 130000, "Cliques": 2800, "Gasto": 4100.0, "CTR (%)": 1.93, "Leads": 112},
            {"age": "35-44", "Impressões": 198000, "Alcance": 178000, "Cliques": 3600, "Gasto": 5800.0, "CTR (%)": 1.82, "Leads": 168},
            {"age": "45-54", "Impressões": 160000, "Alcance": 144000, "Cliques": 2400, "Gasto": 4200.0, "CTR (%)": 1.5, "Leads": 98},
            {"age": "55-64", "Impressões": 88000, "Alcance": 79000, "Cliques": 1100, "Gasto": 2100.0, "CTR (%)": 1.25, "Leads": 32},
            {"age": "65+", "Impressões": 28000, "Alcance": 25000, "Cliques": 340, "Gasto": 800.0, "CTR (%)": 1.21, "Leads": 8},
        ]
        gender_data = [
            {"gender": "male", "Impressões": 352000, "Alcance": 316000, "Cliques": 5900, "Gasto": 10200.0, "CTR (%)": 1.68, "Leads": 218},
            {"gender": "female", "Impressões": 310000, "Alcance": 278000, "Cliques": 5300, "Gasto": 8050.0, "CTR (%)": 1.71, "Leads": 228},
            {"gender": "unknown", "Impressões": 15000, "Alcance": 14000, "Cliques": 220, "Gasto": 200.0, "CTR (%)": 1.47, "Leads": 0},
        ]
        ag_raw = []
        for a in age_data:
            for g in ["male", "female"]:
                ag_raw.append({"age": a["age"], "gender": g,
                               "Impressões": int(a["Impressões"]*0.5), "Gasto": round(a["Gasto"]*0.5,2)})
        return pd.DataFrame(age_data), pd.DataFrame(gender_data), pd.DataFrame(ag_raw)

    def _demo_placement(account_id, date_preset):
        rows = [
            {"Plataforma": "facebook", "Posição": "feed", "Impressões": 280000, "Alcance": 252000, "Cliques": 4800, "Gasto": 8200.0, "CTR (%)": 1.71, "CPC": 1.71, "CPM": 29.29, "Leads": 198},
            {"Plataforma": "instagram", "Posição": "feed", "Impressões": 185000, "Alcance": 166000, "Cliques": 3200, "Gasto": 5400.0, "CTR (%)": 1.73, "CPC": 1.69, "CPM": 29.19, "Leads": 132},
            {"Plataforma": "instagram", "Posição": "story", "Impressões": 130000, "Alcance": 118000, "Cliques": 1900, "Gasto": 2800.0, "CTR (%)": 1.46, "CPC": 1.47, "CPM": 21.54, "Leads": 62},
            {"Plataforma": "facebook", "Posição": "right_hand_column", "Impressões": 52000, "Alcance": 48000, "Cliques": 520, "Gasto": 600.0, "CTR (%)": 1.0, "CPC": 1.15, "CPM": 11.54, "Leads": 18},
            {"Plataforma": "audience_network", "Posição": "classic", "Impressões": 30000, "Alcance": 28000, "Cliques": 800, "Gasto": 450.0, "CTR (%)": 2.67, "CPC": 0.56, "CPM": 15.0, "Leads": 36},
        ]
        return pd.DataFrame(rows)

    def _demo_daily(account_id, date_preset):
        presets = {"last_7d": 7, "last_14d": 14, "last_30d": 30, "last_90d": 90, "this_month": 30, "last_month": 30}
        days = presets.get(date_preset, 30)
        base_spend = 600
        rows = []
        for i in range(days):
            day = _today - _dt.timedelta(days=days-1-i)
            mult = 1 + 0.3*random.gauss(0,1)
            spend = max(200, base_spend*mult)
            imp = int(spend * 22 * (1+0.1*random.gauss(0,1)))
            reach = int(imp * 0.88)
            clicks = int(imp * 0.017 * (1+0.15*random.gauss(0,1)))
            leads = int(spend / 22 * (1+0.2*random.gauss(0,1)))
            rows.append({
                "Data": pd.Timestamp(day),
                "Gasto": round(spend, 2),
                "Impressões": imp, "Alcance": reach, "Cliques": clicks,
                "CTR (%)": round(clicks/imp*100, 2) if imp else 0,
                "CPM": round(spend/imp*1000, 2) if imp else 0,
                "Leads": max(0, leads), "Compras": max(0, int(leads*0.07)),
            })
        return pd.DataFrame(rows)

    # Patch das funções de carregamento para usar dados demo
    load_campaigns = _demo_campaigns
    load_adsets = _demo_adsets
    load_ads = _demo_ads
    load_demographics = _demo_demographics
    load_placement = _demo_placement
    load_daily = _demo_daily

account_labels = {
    acc["id"]: f"{acc.get('name', 'Sem nome')} ({STATUS_MAP.get(acc.get('account_status'), '?')})"
    for acc in accounts
}
account_map = {acc["id"]: acc for acc in accounts}

with st.sidebar:
    st.markdown("""
    <div style="padding:4px 0 12px">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">
        <div style="width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,#1877F2,#42B0FF);display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:900;color:white;box-shadow:0 0 14px rgba(24,119,242,.4)">M</div>
        <div>
          <div style="font-size:15px;font-weight:800;color:#F8FAFC;font-family:'Outfit',sans-serif">316</div>
          <div style="font-size:9px;color:#475569;font-family:'JetBrains Mono',monospace;letter-spacing:2px">META ADS</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    if DEMO_MODE:
        st.markdown("""
        <div style="background:rgba(251,191,36,.1);border:1px solid rgba(251,191,36,.3);border-radius:10px;padding:10px 14px;margin:4px 0 8px">
          <div style="color:#FBBF24;font-size:11px;font-weight:700;letter-spacing:1px;font-family:'JetBrains Mono',monospace">⚠ MODO DEMO</div>
          <div style="color:#94A3B8;font-size:11px;margin-top:2px">Dados simulados — token Meta não configurado ou expirado.</div>
        </div>
        """, unsafe_allow_html=True)
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
    _theme_current = st.session_state.get("theme", "dark")
    _theme_label = "☀️ Modo Claro" if _theme_current == "dark" else "🌙 Modo Escuro"
    if st.button(_theme_label, use_container_width=True):
        st.session_state["theme"] = "light" if _theme_current == "dark" else "dark"
        st.rerun()
    st.divider()
    if st.button("🔄 Atualizar dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.caption("Dados atualizados a cada 5 minutos")

acc_info = account_map[selected_id]
currency = acc_info.get("currency", "BRL")

# ── header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;padding:8px 0 24px;border-bottom:1px solid rgba(255,255,255,.06);margin-bottom:28px">
  <div style="display:flex;align-items:center;gap:14px">
    <div style="width:44px;height:44px;border-radius:14px;background:linear-gradient(135deg,#1877F2 0%,#42B0FF 100%);display:flex;align-items:center;justify-content:center;box-shadow:0 0 20px rgba(24,119,242,.4);font-size:20px;font-weight:900;color:white">M</div>
    <div>
      <h1 style="margin:0;font-size:20px;font-weight:800;letter-spacing:-.5px;color:#F8FAFC;font-family:'Outfit',sans-serif">Meta Ads <span style="color:#38BDF8">Analytics</span></h1>
      <p style="margin:0;font-size:11px;color:#475569;font-family:'JetBrains Mono',monospace">{acc_info.get('name','–')} &nbsp;·&nbsp; {PERIOD_LABELS.get(date_preset,'')}</p>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:10px">
    {'<div style="display:flex;align-items:center;gap:6px;padding:6px 14px;background:rgba(251,191,36,.08);border:1px solid rgba(251,191,36,.25);border-radius:20px"><span style="font-size:11px;color:#FBBF24;font-family:JetBrains Mono,monospace;letter-spacing:1px;font-weight:700">⚠ DEMO</span></div>' if DEMO_MODE else '<div style="display:flex;align-items:center;gap:6px;padding:6px 14px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);border-radius:20px"><div style="width:7px;height:7px;border-radius:50%;background:#34D399;box-shadow:0 0 8px #34D399;animation:pulse-ring 1.5s ease-out infinite"></div><span style="font-size:11px;color:#34D399;font-family:JetBrains Mono,monospace;letter-spacing:1px">LIVE</span></div>'}
    <div style="font-size:11px;color:#334155;font-family:'JetBrains Mono',monospace;padding:6px 14px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:20px">{currency}</div>
  </div>
</div>
""", unsafe_allow_html=True)

if DEMO_MODE:
    st.markdown("""
    <div style="background:linear-gradient(90deg,rgba(251,191,36,.12),rgba(251,191,36,.06));border:1px solid rgba(251,191,36,.3);border-left:4px solid #FBBF24;border-radius:12px;padding:14px 20px;margin-bottom:20px;display:flex;align-items:center;gap:12px">
      <span style="font-size:20px">⚠️</span>
      <div>
        <strong style="color:#FBBF24;font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:2px">MODO DEMONSTRAÇÃO</strong>
        <p style="margin:2px 0 0;color:#94A3B8;font-size:12px">Os dados exibidos são <strong style="color:#E2E8F0">simulados</strong> para fins de demonstração. Para conectar dados reais, configure o token Meta Ads nas configurações do app.</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab_msg, tab_ins = st.tabs([
    "🏦 Conta",
    "📣 Campanhas",
    "🗂️ Conjuntos",
    "🎨 Anúncios",
    "👥 Público",
    "📍 Posicionamento",
    "📅 Evolução Diária",
    "💬 Mensagens",
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
    if DEMO_MODE:
        st.info("📊 **Dados de demonstração** — valores simulados para fins de visualização do layout e funcionalidades.")
    slabel("Informações da Conta")
    spent = safe_float(acc_info.get("amount_spent", 0)) / 100
    balance = safe_float(acc_info.get("balance", 0)) / 100
    spend_cap = safe_float(acc_info.get("spend_cap", 0)) / 100

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Nome", acc_info.get("name", "–"), icon="🏢", color="#818CF8")
    with c2: kpi("Status", STATUS_MAP.get(acc_info.get("account_status"), "?"), icon="🔵", color="#34D399")
    with c3: kpi("Moeda", currency, icon="💱", color="#38BDF8")
    with c4: kpi("Fuso Horário", acc_info.get("timezone_name", "–"), icon="🕐", color="#A78BFA")

    st.markdown("<br>", unsafe_allow_html=True)
    c5, c6, c7, c8 = st.columns(4)
    with c5: kpi("Total Gasto (histórico)", fmt(spent, currency), icon="💸", color="#818CF8")
    with c6: kpi("Saldo Disponível", fmt(balance, currency), icon="🏦", color="#34D399")
    with c7: kpi("Limite de Gasto", fmt(spend_cap, currency) if spend_cap else "Sem limite", icon="⚡", color="#FB923C")
    with c8: kpi("Business", acc_info.get("business_name", "–"), icon="🏢", color="#F472B6")

    st.divider()
    slabel("Todas as Contas Disponíveis")
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
        st.error(f"Erro ao carregar campanhas: {e}")
        df_camp = pd.DataFrame()

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

        slabel("KPIs Gerais")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1: kpi("Total Gasto", fmt(total_spend, currency), icon="💸", color="#818CF8")
        with c2: kpi("Alcance", f"{int(total_reach):,}", icon="👥", color="#A78BFA")
        with c3: kpi("Impressões", f"{int(total_imp):,}", icon="👁️", color="#38BDF8")
        with c4: kpi("Cliques", f"{int(total_clicks):,}", icon="🖱️", color="#34D399")
        with c5: kpi("CTR Médio", f"{avg_ctr:.2f}%", icon="📈", color="#34D399")
        with c6: kpi("CPM Médio", fmt(avg_cpm, currency), icon="📢", color="#FBBF24")

        st.markdown("<br>", unsafe_allow_html=True)
        c7, c8, c9, c10 = st.columns(4)
        with c7: kpi("Frequência Média", f"{avg_freq:.1f}x", icon="🔁", color="#FB923C")
        with c8:
            if total_leads:
                kpi("Total Leads", f"{int(total_leads):,}", icon="🎯", color="#F472B6")
            elif total_purchases:
                kpi("Total Compras", f"{int(total_purchases):,}", icon="🛒", color="#F472B6")
        with c9:
            if total_leads:
                kpi("CPL Médio", fmt(total_spend / total_leads, currency), icon="💡", color="#FB923C")
            elif total_purchases:
                kpi("CPP Médio", fmt(total_spend / total_purchases, currency), icon="💡", color="#FB923C")
        with c10: kpi("Campanhas Ativas", str(len(df_camp)), icon="📣", color="#38BDF8")

        # ── Mensagens KPIs (visíveis se existirem) ──────────────────────────────
        total_conversas = df_camp["Conversas"].sum() if "Conversas" in df_camp.columns else 0
        total_prim_resp = df_camp["Primeiras Respostas"].sum() if "Primeiras Respostas" in df_camp.columns else 0
        if total_conversas > 0:
            st.markdown("<br>", unsafe_allow_html=True)
            slabel("KPIs de Mensagens")
            mc1, mc2, mc3, mc4 = st.columns(4)
            custo_conv_medio = total_spend / total_conversas if total_conversas else 0
            taxa_resp = total_prim_resp / total_conversas * 100 if total_conversas else 0
            total_bloqueios = df_camp["Bloqueios"].sum() if "Bloqueios" in df_camp.columns else 0
            with mc1: kpi("Conversas Iniciadas", f"{int(total_conversas):,}", icon="💬", color="#25D366")
            with mc2: kpi("Custo / Conversa", fmt(custo_conv_medio, currency), icon="💰", color="#25D366")
            with mc3: kpi("Primeiras Respostas", f"{int(total_prim_resp):,}", icon="↩️", color="#34D399")
            with mc4: kpi("Taxa de Resposta", f"{taxa_resp:.1f}%", icon="📊", color="#34D399" if taxa_resp >= 70 else "#FBBF24")

        # ── Funil de conversão ───────────────────────────────────────────────────
        st.divider()
        slabel("Funil de Performance")
        funnel_labels = ["Alcance", "Impressões", "Cliques"]
        funnel_values = [int(total_reach), int(total_imp), int(total_clicks)]
        funnel_colors = ["#818CF8", "#38BDF8", "#34D399"]
        if total_conversas > 0:
            funnel_labels.append("Conversas")
            funnel_values.append(int(total_conversas))
            funnel_colors.append("#25D366")
        if total_leads > 0:
            funnel_labels.append("Leads")
            funnel_values.append(int(total_leads))
            funnel_colors.append("#F472B6")
        if total_purchases > 0:
            funnel_labels.append("Compras")
            funnel_values.append(int(total_purchases))
            funnel_colors.append("#FB923C")
        fig_funnel = go.Figure(go.Funnel(
            y=funnel_labels, x=funnel_values,
            textinfo="value+percent initial",
            marker=dict(color=funnel_colors),
            connector=dict(line=dict(color="rgba(255,255,255,0.1)", dash="dot", width=2)),
        ))
        fig_funnel.update_layout(height=340, title="Funil: do Alcance à Conversão")
        apply_fig(fig_funnel)
        st.plotly_chart(fig_funnel, use_container_width=True)

        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.bar(df_camp.sort_values("Gasto"), x="Gasto", y="Campanha",
                         orientation="h", color="Gasto",
                         color_continuous_scale="Blues", text_auto=".2f",
                         title="Gasto por Campanha", template=CHART_THEME)
            fig.update_layout(coloraxis_showscale=False, height=420)
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.bar(df_camp.sort_values("CTR (%)"), x="CTR (%)", y="Campanha",
                         orientation="h", color="CTR (%)",
                         color_continuous_scale="Greens", text_auto=".2f",
                         title="CTR por Campanha", template=CHART_THEME)
            fig.update_layout(coloraxis_showscale=False, height=420)
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

        col_c, col_d = st.columns(2)
        with col_c:
            fig = go.Figure(layout=dict(template=CHART_THEME))
            fig.add_trace(go.Bar(name="Alcance", x=df_camp["Campanha"], y=df_camp["Alcance"], marker_color="#818CF8"))
            fig.add_trace(go.Bar(name="Impressões", x=df_camp["Campanha"], y=df_camp["Impressões"], marker_color="#38BDF8"))
            fig.update_layout(barmode="group", height=380, xaxis=dict(tickangle=-30), title="Alcance vs Impressões")
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)
        with col_d:
            fig = go.Figure(layout=dict(template=CHART_THEME))
            fig.add_trace(go.Bar(name="CPC", x=df_camp["Campanha"], y=df_camp["CPC"], marker_color="#34D399"))
            fig.add_trace(go.Bar(name="CPM", x=df_camp["Campanha"], y=df_camp["CPM"], marker_color="#A78BFA"))
            fig.update_layout(barmode="group", height=380, xaxis=dict(tickangle=-30), title="CPC vs CPM")
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

        if df_camp["Video Views"].sum() > 0:
            fig = go.Figure(layout=dict(template=CHART_THEME))
            fig.add_trace(go.Bar(name="Video Views", x=df_camp["Campanha"], y=df_camp["Video Views"], marker_color="#FB923C"))
            fig.add_trace(go.Bar(name="ThruPlays", x=df_camp["Campanha"], y=df_camp["ThruPlays"], marker_color="#38BDF8"))
            fig.update_layout(barmode="group", height=350, xaxis=dict(tickangle=-30), title="Video Views vs ThruPlays")
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

        if total_leads > 0:
            df_l = df_camp[df_camp["Leads"] > 0]
            col_e, col_f = st.columns(2)
            with col_e:
                fig = px.pie(df_l, values="Leads", names="Campanha",
                             title="Distribuição de Leads", template=CHART_THEME, hole=0.4)
                apply_fig(fig); st.plotly_chart(fig, use_container_width=True)
            with col_f:
                fig = px.bar(df_l.sort_values("CPL"), x="Campanha", y="CPL",
                             color="CPL", color_continuous_scale="Reds",
                             text_auto=".2f", title="CPL por Campanha", template=CHART_THEME)
                fig.update_layout(coloraxis_showscale=False)
                apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

        if df_camp["Objetivo"].nunique() > 1:
            df_obj = df_camp.groupby("Objetivo")["Gasto"].sum().reset_index()
            fig = px.pie(df_obj, values="Gasto", names="Objetivo",
                         title="Gasto por Objetivo", template=CHART_THEME, hole=0.4)
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

        st.divider()
        slabel("Tabela Completa — Campanhas")
        cols_show = ["Campanha", "Objetivo", "Gasto", "Alcance", "Impressões", "Cliques",
                     "CTR (%)", "CPC", "CPM", "Frequência", "Leads", "CPL", "Compras", "CPP Compra",
                     "Video Views", "ThruPlays"]
        _styled_camp = df_camp[cols_show].style.format({
            "Gasto": "{:.2f}", "CPC": "{:.2f}", "CPM": "{:.2f}",
            "CTR (%)": "{:.2f}", "Frequência": "{:.1f}", "CPL": "{:.2f}", "CPP Compra": "{:.2f}",
        })
        _styled_camp = _styled_camp.background_gradient(subset=["Gasto"], cmap="Blues")
        _styled_camp = _styled_camp.background_gradient(subset=["CTR (%)"], cmap="Greens")
        st.dataframe(_styled_camp, use_container_width=True, height=400)
        csv = df_camp.drop(columns=["Todas Ações"]).to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar Campanhas CSV", csv, "campanhas.csv", "text/csv")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CONJUNTOS
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    try:
        df_adset = load_adsets(selected_id, date_preset)
    except Exception as e:
        st.error(f"Erro ao carregar conjuntos: {e}")
        df_adset = pd.DataFrame()

    df_adset = apply_camp_filter(df_adset)

    if selected_campaigns:
        st.info(f"🎯 Filtrando por campanhas: **{', '.join(selected_campaigns)}**")

    if df_adset.empty:
        st.warning("Nenhum conjunto no período.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1: kpi("Total Conjuntos", str(len(df_adset)), icon="🗂️", color="#38BDF8")
        with c2: kpi("Total Gasto", fmt(df_adset["Gasto"].sum(), currency), icon="💸", color="#818CF8")
        with c3: kpi("Total Leads", f"{int(df_adset['Leads'].sum()):,}", icon="🎯", color="#F472B6")
        with c4: kpi("CTR Médio", f"{df_adset['CTR (%)'].mean():.2f}%", icon="📈", color="#34D399")

        st.markdown("<br>", unsafe_allow_html=True)
        fig = px.bar(df_adset.sort_values("Gasto").head(20), x="Gasto", y="Conjunto",
                     orientation="h", color="Gasto", color_continuous_scale="Purples",
                     hover_data=["Campanha", "CTR (%)", "CPL"],
                     title="Top 20 Conjuntos por Gasto", template=CHART_THEME)
        fig.update_layout(coloraxis_showscale=False, height=500)
        apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.scatter(df_adset, x="Gasto", y="CTR (%)", size="Impressões",
                             color="CPM", hover_name="Conjunto",
                             title="Gasto vs CTR (tamanho = Impressões)",
                             template=CHART_THEME)
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.scatter(df_adset, x="CPC", y="CTR (%)", size="Cliques",
                             color="Frequência", hover_name="Conjunto",
                             title="CPC vs CTR (tamanho = Cliques)",
                             template=CHART_THEME)
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

        slabel("Tabela Completa — Conjuntos")
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
        st.error(f"Erro ao carregar anúncios: {e}")
        df_ads = pd.DataFrame()

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
            fig.update_layout(height=max(400, len(top20) * 28), yaxis=dict(title=""))
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

            col_a, col_b = st.columns(2)
            with col_a:
                fig = px.scatter(df_filtered, x="Gasto", y="CTR (%)", size="Impressões",
                                 color="CPC", hover_name="Anúncio",
                                 hover_data=["Campanha", "Conjunto"],
                                 title="Gasto vs CTR (tamanho = Impressões)", template=CHART_THEME)
                apply_fig(fig); st.plotly_chart(fig, use_container_width=True)
            with col_b:
                fig = px.scatter(df_filtered, x="CPM", y="CTR (%)", size="Cliques",
                                 color="Frequência", hover_name="Anúncio",
                                 hover_data=["Campanha", "Conjunto"],
                                 title="CPM vs CTR (tamanho = Cliques)", template=CHART_THEME)
                apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

            if df_filtered["Video Views"].sum() > 0:
                df_vid = df_filtered[df_filtered["Video Views"] > 0].sort_values("Video Views").tail(15)
                col_v1, col_v2 = st.columns(2)
                with col_v1:
                    fig = px.bar(df_vid, x="Video Views", y="Anúncio", orientation="h",
                                 color="Video Views", color_continuous_scale="Oranges",
                                 title="Video Views por Anúncio", template=CHART_THEME)
                    fig.update_layout(coloraxis_showscale=False)
                    apply_fig(fig); st.plotly_chart(fig, use_container_width=True)
                with col_v2:
                    fig = px.bar(df_vid, x="ThruPlays", y="Anúncio", orientation="h",
                                 color="ThruPlays", color_continuous_scale="Teal",
                                 title="ThruPlays por Anúncio", template=CHART_THEME)
                    fig.update_layout(coloraxis_showscale=False)
                    apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

            if df_filtered["Leads"].sum() > 0:
                df_leads_ad = df_filtered[df_filtered["Leads"] > 0].sort_values("CPL")
                fig = px.bar(df_leads_ad.head(15), x="Anúncio", y="CPL",
                             color="Leads", color_continuous_scale="Purples",
                             title="CPL por Anúncio (top 15)", template=CHART_THEME)
                fig.update_layout(xaxis=dict(tickangle=-30))
                apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

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
            _styled_ads = df_filtered[cols_show_ads].style.format({
                "Gasto": "{:.2f}", "CPC": "{:.2f}", "CPM": "{:.2f}",
                "CTR (%)": "{:.2f}", "Frequência": "{:.1f}", "CPL": "{:.2f}", "CPP": "{:.2f}",
            })
            _styled_ads = _styled_ads.background_gradient(subset=["Gasto"], cmap="Oranges")
            _styled_ads = _styled_ads.background_gradient(subset=["CTR (%)"], cmap="RdYlGn")
            st.dataframe(_styled_ads, use_container_width=True, height=520)

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
        st.error(f"Erro ao carregar dados demográficos: {e}")
        df_age, df_gender, df_ag = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    st.subheader("Por Faixa Etária")
    if not df_age.empty:
        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.bar(df_age, x="age", y="Impressões", color="Impressões",
                         color_continuous_scale="Blues",
                         title="Impressões por Idade", template=CHART_THEME)
            fig.update_layout(coloraxis_showscale=False)
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.bar(df_age, x="age", y="Gasto", color="Gasto",
                         color_continuous_scale="Reds",
                         title="Gasto por Idade", template=CHART_THEME)
            fig.update_layout(coloraxis_showscale=False)
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

        col_c, col_d = st.columns(2)
        with col_c:
            fig = px.bar(df_age, x="age", y="CTR (%)", color="CTR (%)",
                         color_continuous_scale="Greens",
                         title="CTR por Idade", template=CHART_THEME)
            fig.update_layout(coloraxis_showscale=False)
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)
        with col_d:
            if df_age["Leads"].sum() > 0:
                fig = px.bar(df_age[df_age["Leads"] > 0], x="age", y="Leads",
                             color="Leads", color_continuous_scale="Purples",
                             title="Leads por Idade", template=CHART_THEME)
                fig.update_layout(coloraxis_showscale=False)
                apply_fig(fig); st.plotly_chart(fig, use_container_width=True)
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
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.pie(df_gender, values="Gasto", names="Gênero",
                         title="Gasto", template=CHART_THEME, hole=0.4)
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)
        with col_c:
            fig = px.bar(df_gender, x="Gênero", y="CTR (%)", color="Gênero",
                         title="CTR por Gênero", template=CHART_THEME)
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_gender.drop(columns=["gender"]), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Mapa de Calor — Gasto por Idade × Gênero")
    if not df_ag.empty:
        gender_label = {"male": "Masculino", "female": "Feminino", "unknown": "Desconhecido"}
        df_ag["gender"] = df_ag["gender"].map(gender_label).fillna(df_ag["gender"])
        pivot = df_ag.pivot_table(index="age", columns="gender", values="Gasto", aggfunc="sum", fill_value=0)
        fig = px.imshow(pivot, text_auto=".1f", color_continuous_scale="RdYlGn",
                        title="Gasto por Faixa Etária × Gênero", template=CHART_THEME)
        apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 — POSICIONAMENTO
# ═══════════════════════════════════════════════════════════════════════════════
with tab6:
    try:
        df_place = load_placement(selected_id, date_preset)
    except Exception as e:
        st.error(f"Erro ao carregar posicionamentos: {e}")
        df_place = pd.DataFrame()

    if df_place.empty:
        st.warning("Nenhum dado de posicionamento.")
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.pie(df_place, values="Gasto", names="Plataforma",
                         title="Gasto por Plataforma", template=CHART_THEME, hole=0.4)
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.pie(df_place, values="Impressões", names="Plataforma",
                         title="Impressões por Plataforma", template=CHART_THEME, hole=0.4)
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

        fig = px.bar(df_place.sort_values("CTR (%)"), x="CTR (%)",
                     y=df_place["Plataforma"] + " / " + df_place["Posição"],
                     orientation="h", color="CTR (%)", color_continuous_scale="Greens",
                     text_auto=".2f", title="CTR por Posicionamento", template=CHART_THEME)
        fig.update_layout(coloraxis_showscale=False, height=500)
        apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

        col_c, col_d = st.columns(2)
        with col_c:
            fig = px.bar(df_place, x="Plataforma", y="Gasto", color="Posição",
                         title="Gasto por Plataforma e Posição", template=CHART_THEME)
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)
        with col_d:
            fig = px.bar(df_place, x="Plataforma", y="CPC", color="Posição",
                         barmode="group", title="CPC por Plataforma e Posição", template=CHART_THEME)
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

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
        st.error(f"Erro ao carregar dados diários: {e}")
        df_daily = pd.DataFrame()

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
        apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.line(df_daily, x="Data", y="CTR (%)", markers=True,
                          title="CTR Diário (%)", template=CHART_THEME)
            fig.update_traces(line_color="#48bb78")
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.line(df_daily, x="Data", y="CPM", markers=True,
                          title="CPM Diário", template=CHART_THEME)
            fig.update_traces(line_color="#EF553B")
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

        col_c, col_d = st.columns(2)
        with col_c:
            fig = px.bar(df_daily, x="Data", y="Impressões",
                         title="Impressões Diárias", template=CHART_THEME,
                         color="Impressões", color_continuous_scale="Blues")
            fig.update_layout(coloraxis_showscale=False)
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)
        with col_d:
            fig = px.bar(df_daily, x="Data", y="Cliques",
                         title="Cliques Diários", template=CHART_THEME,
                         color="Cliques", color_continuous_scale="Greens")
            fig.update_layout(coloraxis_showscale=False)
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

        if df_daily["Leads"].sum() > 0:
            fig = px.bar(df_daily, x="Data", y="Leads", title="Leads por Dia",
                         color="Leads", color_continuous_scale="Purples", template=CHART_THEME)
            fig.update_layout(coloraxis_showscale=False)
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

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
# TAB 8 — MENSAGENS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_msg:
    try:
        df_msg = load_campaigns(selected_id, date_preset)
        df_msg_adset = load_adsets(selected_id, date_preset)
        df_msg_ads = load_ads(selected_id, date_preset)
    except Exception as e:
        st.error(f"Erro ao carregar dados de mensagens: {e}")
        df_msg = pd.DataFrame()

    df_msg = apply_camp_filter(df_msg)
    df_msg_adset = apply_camp_filter(df_msg_adset)
    df_msg_ads = apply_camp_filter(df_msg_ads)

    has_msg = "Conversas" in df_msg.columns and df_msg["Conversas"].sum() > 0

    if not has_msg:
        st.markdown("""
        <div style="background:rgba(37,211,102,.06);border:1px solid rgba(37,211,102,.2);border-left:4px solid #25D366;border-radius:12px;padding:28px 24px;margin:20px 0;text-align:center">
          <div style="font-size:2rem;margin-bottom:10px">💬</div>
          <strong style="color:#25D366;font-size:1.1rem">Nenhuma campanha de Mensagens no período</strong>
          <p style="color:#94A3B8;margin:8px 0 0;font-size:.9rem">Para ver métricas de mensagens, crie campanhas com objetivo <strong style="color:#E2E8F0">MESSAGES</strong> no Meta Ads Manager com destino WhatsApp, Messenger ou Instagram Direct.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        df_msg_camp = df_msg[df_msg["Conversas"] > 0].copy()

        # ── KPIs Principais ──────────────────────────────────────────────────
        slabel("KPIs de Mensagens")
        total_conv     = int(df_msg_camp["Conversas"].sum())
        total_pr       = int(df_msg_camp["Primeiras Respostas"].sum())
        total_bloq     = int(df_msg_camp["Bloqueios"].sum()) if "Bloqueios" in df_msg_camp.columns else 0
        total_gasto_m  = df_msg_camp["Gasto"].sum()
        custo_conv_m   = total_gasto_m / total_conv if total_conv else 0
        taxa_resp_m    = total_pr / total_conv * 100 if total_conv else 0
        taxa_bloq_m    = total_bloq / total_conv * 100 if total_conv else 0

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1: kpi("Conversas Iniciadas",  f"{total_conv:,}",          icon="💬", color="#25D366")
        with c2: kpi("Custo / Conversa",     fmt(custo_conv_m, currency), icon="💰", color="#25D366")
        with c3: kpi("Primeiras Respostas",  f"{total_pr:,}",             icon="↩️", color="#34D399")
        with c4: kpi("Taxa de Resposta",     f"{taxa_resp_m:.1f}%",       icon="📊", color="#34D399" if taxa_resp_m >= 70 else "#FBBF24")
        with c5: kpi("Bloqueios",            f"{total_bloq:,}",           icon="🚫", color="#F87171" if total_bloq > 0 else "#94A3B8")
        with c6: kpi("Taxa de Bloqueio",     f"{taxa_bloq_m:.1f}%",       icon="⚠️", color="#F87171" if taxa_bloq_m > 5 else "#34D399")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Qualidade das Conversas ────────────────────────────────────────
        slabel("Qualidade de Engajamento")
        qual_col1, qual_col2, qual_col3 = st.columns(3)

        with qual_col1:
            # Funil de mensagens
            funnel_m = go.Figure(go.Funnel(
                y=["Cliques", "Conversas Iniciadas", "Primeiras Respostas"],
                x=[int(df_msg_camp["Cliques"].sum()), total_conv, total_pr],
                textinfo="value+percent initial",
                marker=dict(color=["#38BDF8", "#25D366", "#34D399"]),
                connector=dict(line=dict(color="rgba(255,255,255,0.1)", dash="dot", width=2)),
            ))
            funnel_m.update_layout(height=300, title="Funil de Mensagens")
            apply_fig(funnel_m)
            st.plotly_chart(funnel_m, use_container_width=True)

        with qual_col2:
            # Gauge - Taxa de resposta
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=taxa_resp_m,
                number={"suffix": "%", "font": {"size": 28, "color": "#F8FAFC"}},
                delta={"reference": 70, "increasing": {"color": "#34D399"}, "decreasing": {"color": "#F87171"}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#475569"},
                    "bar": {"color": "#25D366"},
                    "steps": [
                        {"range": [0, 40], "color": "rgba(248,113,113,0.15)"},
                        {"range": [40, 70], "color": "rgba(251,191,36,0.15)"},
                        {"range": [70, 100], "color": "rgba(52,211,153,0.15)"},
                    ],
                    "threshold": {"line": {"color": "#38BDF8", "width": 3}, "thickness": 0.8, "value": 70},
                },
                title={"text": "Taxa de Resposta", "font": {"color": "#94A3B8"}},
            ))
            fig_gauge.update_layout(height=300, paper_bgcolor="rgba(255,255,255,0.02)", font_color="#94A3B8")
            st.plotly_chart(fig_gauge, use_container_width=True)

        with qual_col3:
            # Gauge - Taxa de bloqueio
            fig_bloq = go.Figure(go.Indicator(
                mode="gauge+number",
                value=taxa_bloq_m,
                number={"suffix": "%", "font": {"size": 28, "color": "#F8FAFC"}},
                gauge={
                    "axis": {"range": [0, 20], "tickcolor": "#475569"},
                    "bar": {"color": "#F87171" if taxa_bloq_m > 5 else "#34D399"},
                    "steps": [
                        {"range": [0, 3], "color": "rgba(52,211,153,0.15)"},
                        {"range": [3, 7], "color": "rgba(251,191,36,0.15)"},
                        {"range": [7, 20], "color": "rgba(248,113,113,0.15)"},
                    ],
                    "threshold": {"line": {"color": "#FBBF24", "width": 3}, "thickness": 0.8, "value": 5},
                },
                title={"text": "Taxa de Bloqueio (meta: < 5%)", "font": {"color": "#94A3B8"}},
            ))
            fig_bloq.update_layout(height=300, paper_bgcolor="rgba(255,255,255,0.02)", font_color="#94A3B8")
            st.plotly_chart(fig_bloq, use_container_width=True)

        st.divider()

        # ── Análise por Campanha ────────────────────────────────────────────
        slabel("Performance por Campanha")
        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.bar(df_msg_camp.sort_values("Conversas"), x="Conversas", y="Campanha",
                         orientation="h", color="Conversas", color_continuous_scale=[[0, "#1a3d2b"], [1, "#25D366"]],
                         text_auto=True, title="Conversas por Campanha", template=CHART_THEME)
            fig.update_layout(coloraxis_showscale=False, height=360)
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.bar(df_msg_camp.sort_values("Custo/Conversa"), x="Custo/Conversa", y="Campanha",
                         orientation="h", color="Custo/Conversa", color_continuous_scale="RdYlGn_r",
                         text_auto=".2f", title="Custo por Conversa (menor = melhor)", template=CHART_THEME)
            fig.update_layout(coloraxis_showscale=False, height=360)
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

        col_c, col_d = st.columns(2)
        with col_c:
            fig = px.bar(df_msg_camp, x="Campanha", y=["Conversas", "Primeiras Respostas"],
                         barmode="group", title="Conversas vs Primeiras Respostas",
                         color_discrete_map={"Conversas": "#25D366", "Primeiras Respostas": "#34D399"},
                         template=CHART_THEME)
            fig.update_layout(height=340, xaxis=dict(tickangle=-20))
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)
        with col_d:
            fig = px.scatter(df_msg_camp, x="Gasto", y="Conversas",
                             size="Primeiras Respostas", color="Taxa Resposta (%)",
                             hover_name="Campanha", color_continuous_scale="Greens",
                             title="Gasto vs Conversas (tamanho = Primeiras Respostas)",
                             template=CHART_THEME)
            apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

        # ── Análise por Conjunto ────────────────────────────────────────────
        if "Conversas" in df_msg_adset.columns:
            df_adset_msg = df_msg_adset[df_msg_adset["Conversas"] > 0]
            if not df_adset_msg.empty:
                st.divider()
                slabel("Performance por Conjunto de Anúncios")
                col_e, col_f = st.columns(2)
                with col_e:
                    fig = px.bar(df_adset_msg.sort_values("Conversas"), x="Conversas", y="Conjunto",
                                 orientation="h", color="Custo/Conversa", color_continuous_scale="RdYlGn_r",
                                 hover_data=["Campanha", "Taxa Resposta (%)"],
                                 title="Conversas por Conjunto (cor = Custo/Conversa)", template=CHART_THEME)
                    fig.update_layout(coloraxis_showscale=True, height=380)
                    apply_fig(fig); st.plotly_chart(fig, use_container_width=True)
                with col_f:
                    fig = px.scatter(df_adset_msg, x="Custo/Conversa", y="Taxa Resposta (%)",
                                     size="Conversas", color="Bloqueios",
                                     hover_name="Conjunto",
                                     title="Custo/Conversa vs Taxa de Resposta",
                                     color_continuous_scale="Reds", template=CHART_THEME)
                    apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

        # ── Análise por Anúncio ─────────────────────────────────────────────
        if "Conversas" in df_msg_ads.columns:
            df_ads_msg = df_msg_ads[df_msg_ads["Conversas"] > 0]
            if not df_ads_msg.empty:
                st.divider()
                slabel("Top Anúncios — Mensagens")
                top_conv = df_ads_msg.sort_values("Conversas", ascending=False).head(10)
                fig = px.bar(top_conv, x="Anúncio", y="Conversas",
                             color="Custo/Conversa", color_continuous_scale="RdYlGn_r",
                             hover_data=["Conjunto", "Campanha", "Taxa Resposta (%)"],
                             title="Top 10 Anúncios por Conversas (cor = Custo/Conversa)",
                             template=CHART_THEME)
                fig.update_layout(xaxis=dict(tickangle=-25), coloraxis_showscale=True)
                apply_fig(fig); st.plotly_chart(fig, use_container_width=True)

        # ── Insights de Mensagens ───────────────────────────────────────────
        st.divider()
        slabel("Diagnóstico de Qualidade")
        ic1, ic2 = st.columns(2)
        with ic1:
            if taxa_resp_m >= 80:
                insight("good", "✅", "Taxa de Resposta Excelente",
                        f"<strong>{taxa_resp_m:.1f}%</strong> das conversas geraram uma primeira resposta. Seu público está altamente engajado com o conteúdo.")
            elif taxa_resp_m >= 60:
                insight("warn", "📊", "Taxa de Resposta Razoável",
                        f"<strong>{taxa_resp_m:.1f}%</strong> de taxa de resposta. Melhore o criativo e a mensagem de boas-vindas para aumentar o engajamento.")
            else:
                insight("bad", "🚨", "Taxa de Resposta Crítica",
                        f"Apenas <strong>{taxa_resp_m:.1f}%</strong> das conversas recebem resposta. Revise urgentemente a mensagem automática de boas-vindas e a qualidade do público.")

            if custo_conv_m > 0:
                if custo_conv_m < 15:
                    insight("good", "💰", "Custo por Conversa Competitivo",
                            f"Custo médio de <strong>{fmt(custo_conv_m, currency)}</strong> por conversa. Excelente eficiência para campanhas de mensagens no Brasil.")
                elif custo_conv_m < 30:
                    insight("warn", "💡", "Custo por Conversa Moderado",
                            f"Custo médio de <strong>{fmt(custo_conv_m, currency)}</strong>. Há espaço para otimizar via melhor segmentação e criativos mais atrativos.")
                else:
                    insight("bad", "🚨", "Custo por Conversa Alto",
                            f"Custo de <strong>{fmt(custo_conv_m, currency)}</strong> por conversa está acima do esperado. Revise segmentação e criativos imediatamente.")
        with ic2:
            if taxa_bloq_m > 7:
                insight("bad", "🚫", "Taxa de Bloqueio Alarmante",
                        f"<strong>{taxa_bloq_m:.1f}%</strong> dos usuários estão bloqueando após a conversa. Isso sinaliza que o público não está qualificado ou a abordagem é invasiva.")
            elif taxa_bloq_m > 3:
                insight("warn", "⚠️", "Taxa de Bloqueio Elevada",
                        f"<strong>{taxa_bloq_m:.1f}%</strong> de bloqueios. Revise a qualidade do público-alvo e o tom da comunicação.")
            else:
                insight("good", "✅", "Taxa de Bloqueio Saudável",
                        f"Apenas <strong>{taxa_bloq_m:.1f}%</strong> de bloqueios. Seu público está bem segmentado e receptivo à comunicação.")

            if len(df_msg_camp) > 1 and "Custo/Conversa" in df_msg_camp.columns:
                melhor = df_msg_camp.loc[df_msg_camp["Custo/Conversa"].replace(0, float("inf")).idxmin()]
                insight("good", "🏆", "Melhor Campanha por Custo/Conversa",
                        f"<strong>{melhor['Campanha']}</strong> com custo de {fmt(melhor['Custo/Conversa'], currency)}/conversa e {int(melhor['Conversas'])} conversas. Priorize esta campanha.")

        # ── Tabela completa ─────────────────────────────────────────────────
        st.divider()
        slabel("Tabela Detalhada — Mensagens por Campanha")
        msg_cols = ["Campanha", "Gasto", "Impressões", "Cliques", "CTR (%)",
                    "Conversas", "Custo/Conversa", "Primeiras Respostas", "Taxa Resposta (%)", "Bloqueios"]
        msg_cols_avail = [c for c in msg_cols if c in df_msg_camp.columns]
        _styled_msg = df_msg_camp[msg_cols_avail].style.format({
            "Gasto": "{:.2f}", "CTR (%)": "{:.2f}", "Custo/Conversa": "{:.2f}", "Taxa Resposta (%)": "{:.1f}",
        })
        _styled_msg = _styled_msg.background_gradient(subset=["Conversas"], cmap="Greens")
        if "Custo/Conversa" in msg_cols_avail:
            _styled_msg = _styled_msg.background_gradient(subset=["Custo/Conversa"], cmap="RdYlGn_r")
        st.dataframe(_styled_msg, use_container_width=True, height=380)
        csv_msg = df_msg_camp[msg_cols_avail].to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar Mensagens CSV", csv_msg, "mensagens.csv", "text/csv")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 9 — INSIGHTS & RECOMENDAÇÕES
# ═══════════════════════════════════════════════════════════════════════════════
with tab_ins:
    st.markdown("## 🧠 Insights & Recomendações")
    st.caption(f"Análise automática baseada no período: **{PERIOD_LABELS[date_preset]}**")

    # Carrega dados necessários (pré-inicializa para evitar NameError)
    df_camp_i = pd.DataFrame()
    df_adset_i = pd.DataFrame()
    df_ads_i = pd.DataFrame()
    df_daily_i = pd.DataFrame()
    df_age_i, df_gender_i = pd.DataFrame(), pd.DataFrame()
    df_place_i = pd.DataFrame()
    try:
        df_camp_i = load_campaigns(selected_id, date_preset)
        df_adset_i = load_adsets(selected_id, date_preset)
        df_ads_i = load_ads(selected_id, date_preset)
        df_daily_i = load_daily(selected_id, date_preset)
        try:
            df_age_i, df_gender_i, _ = load_demographics(selected_id, date_preset)
        except Exception:
            pass
        try:
            df_place_i = load_placement(selected_id, date_preset)
        except Exception:
            pass
    except Exception as e:
        st.error(f"Erro ao carregar dados para insights: {e}")

    if df_camp_i.empty:
        st.warning("Sem dados suficientes para gerar insights no período selecionado.")
        st.stop()  # último tab — seguro parar aqui

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

        # Mensagens
        if "Conversas" in df_camp_i.columns:
            total_conv_i = df_camp_i["Conversas"].sum()
            total_pr_i = df_camp_i["Primeiras Respostas"].sum() if "Primeiras Respostas" in df_camp_i.columns else 0
            if total_conv_i > 0:
                taxa_r_i = total_pr_i / total_conv_i * 100 if total_conv_i else 0
                custo_c_i = total_spend_i / total_conv_i
                insight("info", "💬", f"Mensagens: {int(total_conv_i):,} Conversas",
                        f"Custo médio por conversa: <strong>{fmt(custo_c_i, currency)}</strong> — Taxa de resposta: <strong>{taxa_r_i:.1f}%</strong>. Acesse a aba 💬 Mensagens para análise completa.")
                df_bloq_i = df_camp_i[df_camp_i.get("Bloqueios", pd.Series([0]*len(df_camp_i))) > 0] if "Bloqueios" in df_camp_i.columns else pd.DataFrame()
                total_bloq_i = df_camp_i["Bloqueios"].sum() if "Bloqueios" in df_camp_i.columns else 0
                taxa_bloq_i = total_bloq_i / total_conv_i * 100 if total_conv_i else 0
                if taxa_bloq_i > 5:
                    insight("bad", "🚫", "Taxa de Bloqueio Alarmante nas Mensagens",
                            f"<strong>{taxa_bloq_i:.1f}%</strong> de bloqueios. Revise a qualidade do público e a abordagem da comunicação.")

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
    if "Conversas" in df_camp_i.columns and df_camp_i["Conversas"].sum() > 0:
        df_conv_i = df_camp_i[df_camp_i["Conversas"] > 0]
        taxa_r_acao = df_conv_i["Primeiras Respostas"].sum() / df_conv_i["Conversas"].sum() * 100 if df_conv_i["Conversas"].sum() > 0 else 0
        if taxa_r_acao < 60:
            acoes.append(("🔴 Alta Prioridade", f"Taxa de resposta nas mensagens em {taxa_r_acao:.0f}% — revise mensagem de boas-vindas e qualidade do público"))
        if "Bloqueios" in df_camp_i.columns:
            taxa_b = df_camp_i["Bloqueios"].sum() / df_camp_i["Conversas"].sum() * 100
            if taxa_b > 5:
                acoes.append(("🔴 Alta Prioridade", f"Taxa de bloqueio de {taxa_b:.1f}% nas campanhas de mensagens — revise segmentação e abordagem"))
        if len(df_conv_i) > 1:
            best_msg = df_conv_i.loc[df_conv_i["Custo/Conversa"].replace(0, float("inf")).idxmin()]
            acoes.append(("🟢 Oportunidade", f"Escalar campanha de mensagens '{best_msg['Campanha']}' — menor Custo/Conversa ({fmt(best_msg['Custo/Conversa'], currency)})"))

    if acoes:
        for prioridade, acao in acoes:
            cor = "bad" if "Alta" in prioridade else "warn" if "Média" in prioridade else "good"
            insight(cor, "", prioridade, acao)
    else:
        insight("good", "✅", "Conta em bom estado", "Nenhuma ação crítica identificada. Continue monitorando e testando novos criativos regularmente.")

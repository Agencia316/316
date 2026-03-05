import os
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.user import User

load_dotenv()

APP_ID = os.getenv("FB_APP_ID")
APP_SECRET = os.getenv("FB_APP_SECRET")
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")


def init_api():
    FacebookAdsApi.init(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        access_token=ACCESS_TOKEN,
    )


def get_ad_accounts():
    me = User(fbid="me")
    return list(me.get_ad_accounts(fields=["id", "name", "currency", "account_status"]))


def get_campaign_insights_30d(ad_account_id):
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
            "date_preset": "last_30d",
            "level": "campaign",
            "sort": ["spend_descending"],
        },
    )
    return list(insights)


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
            return float(a.get("value", 0))
    return None


def format_currency(value, currency="BRL"):
    symbol = "R$" if currency == "BRL" else "$"
    return f"{symbol} {float(value):,.2f}"


def analyze(ad_account_id, currency="BRL"):
    print(f"\n{'='*60}")
    print(f"  ANALISE DE CAMPANHAS - ULTIMOS 30 DIAS")
    print(f"  Conta: {ad_account_id}")
    print(f"{'='*60}\n")

    campaigns = get_campaign_insights_30d(ad_account_id)

    if not campaigns:
        print("Nenhuma campanha com dados nos ultimos 30 dias.")
        return

    total_spend = 0
    total_impressions = 0
    total_clicks = 0
    total_reach = 0
    total_leads = 0
    total_purchases = 0

    rows = []
    for c in campaigns:
        spend = float(c.get("spend", 0))
        impressions = int(c.get("impressions", 0))
        clicks = int(c.get("clicks", 0))
        reach = int(c.get("reach", 0))
        ctr = float(c.get("ctr", 0))
        cpc = float(c.get("cpc", 0)) if c.get("cpc") else 0
        cpm = float(c.get("cpm", 0)) if c.get("cpm") else 0
        frequency = float(c.get("frequency", 0)) if c.get("frequency") else 0
        actions = c.get("actions", [])
        cpa_list = c.get("cost_per_action_type", [])

        leads = extract_action(actions, "lead") or extract_action(actions, "onsite_conversion.lead_grouped")
        purchases = extract_action(actions, "purchase")
        link_clicks = extract_action(actions, "link_click")
        cpl = extract_cost_per_action(cpa_list, "lead")
        cpp = extract_cost_per_action(cpa_list, "purchase")

        total_spend += spend
        total_impressions += impressions
        total_clicks += clicks
        total_reach += reach
        total_leads += leads
        total_purchases += purchases

        rows.append({
            "name": c.get("campaign_name", ""),
            "spend": spend,
            "impressions": impressions,
            "reach": reach,
            "clicks": clicks,
            "ctr": ctr,
            "cpc": cpc,
            "cpm": cpm,
            "frequency": frequency,
            "leads": leads,
            "purchases": purchases,
            "link_clicks": link_clicks,
            "cpl": cpl,
            "cpp": cpp,
        })

    # --- Resumo Geral ---
    print("RESUMO GERAL")
    print("-" * 40)
    print(f"  Total gasto:        {format_currency(total_spend, currency)}")
    print(f"  Alcance total:      {total_reach:,}")
    print(f"  Impressoes totais:  {total_impressions:,}")
    print(f"  Cliques totais:     {total_clicks:,}")
    avg_ctr = (total_clicks / total_impressions * 100) if total_impressions else 0
    avg_cpm = (total_spend / total_impressions * 1000) if total_impressions else 0
    print(f"  CTR medio:          {avg_ctr:.2f}%")
    print(f"  CPM medio:          {format_currency(avg_cpm, currency)}")
    if total_leads:
        print(f"  Total leads:        {total_leads:,}")
        cpl_geral = total_spend / total_leads
        print(f"  CPL medio:          {format_currency(cpl_geral, currency)}")
    if total_purchases:
        print(f"  Total compras:      {total_purchases:,}")
        cpp_geral = total_spend / total_purchases
        print(f"  CPP medio:          {format_currency(cpp_geral, currency)}")

    # --- Detalhamento por Campanha ---
    print(f"\n{'='*60}")
    print("DETALHAMENTO POR CAMPANHA (ordenado por gasto)")
    print(f"{'='*60}")

    for i, r in enumerate(rows, 1):
        print(f"\n[{i}] {r['name']}")
        print(f"    Gasto:        {format_currency(r['spend'], currency)}")
        print(f"    Alcance:      {r['reach']:,}  |  Impressoes: {r['impressions']:,}  |  Freq: {r['frequency']:.1f}x")
        print(f"    Cliques:      {r['clicks']:,}  |  CTR: {r['ctr']:.2f}%  |  CPC: {format_currency(r['cpc'], currency)}")
        print(f"    CPM:          {format_currency(r['cpm'], currency)}")
        if r["leads"]:
            cpl_str = format_currency(r["cpl"], currency) if r["cpl"] else "N/A"
            print(f"    Leads:        {r['leads']:,}  |  CPL: {cpl_str}")
        if r["purchases"]:
            cpp_str = format_currency(r["cpp"], currency) if r["cpp"] else "N/A"
            print(f"    Compras:      {r['purchases']:,}  |  CPP: {cpp_str}")

    # --- Rankings ---
    print(f"\n{'='*60}")
    print("RANKINGS")
    print(f"{'='*60}")

    if len(rows) > 1:
        best_ctr = max(rows, key=lambda x: x["ctr"])
        worst_ctr = min(rows, key=lambda x: x["ctr"])
        print(f"\n  Melhor CTR:  {best_ctr['name']} ({best_ctr['ctr']:.2f}%)")
        print(f"  Pior CTR:    {worst_ctr['name']} ({worst_ctr['ctr']:.2f}%)")

        most_spend = rows[0]
        print(f"\n  Maior gasto: {most_spend['name']} ({format_currency(most_spend['spend'], currency)})")

        leads_rows = [r for r in rows if r["leads"] > 0 and r["cpl"]]
        if leads_rows:
            best_cpl = min(leads_rows, key=lambda x: x["cpl"])
            worst_cpl = max(leads_rows, key=lambda x: x["cpl"])
            print(f"\n  Melhor CPL:  {best_cpl['name']} ({format_currency(best_cpl['cpl'], currency)})")
            print(f"  Pior CPL:    {worst_cpl['name']} ({format_currency(worst_cpl['cpl'], currency)})")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    init_api()
    print("Conectando a API do Facebook...")

    accounts = get_ad_accounts()
    if not accounts:
        print("Nenhuma conta de anuncio encontrada.")
        exit(1)

    print("\nContas de anuncio disponiveis:")
    print("-" * 50)
    for i, acc in enumerate(accounts, 1):
        status_map = {1: "ATIVA", 2: "DESATIVADA", 3: "SUSPENSA", 7: "PENDENTE", 9: "EM REVISAO"}
        status = status_map.get(acc.get("account_status"), "DESCONHECIDO")
        print(f"  [{i}] {acc.get('name', 'Sem nome')}")
        print(f"      ID: {acc['id']}  |  Moeda: {acc.get('currency', '?')}  |  Status: {status}")
    print("-" * 50)

    escolha = input("\nDigite o numero da conta que deseja analisar (ou 'todas'): ").strip()

    if escolha.lower() == "todas":
        for acc in accounts:
            analyze(acc["id"], acc.get("currency", "BRL"))
    else:
        try:
            idx = int(escolha) - 1
            if 0 <= idx < len(accounts):
                acc = accounts[idx]
                analyze(acc["id"], acc.get("currency", "BRL"))
            else:
                print("Numero invalido.")
                exit(1)
        except ValueError:
            print("Entrada invalida.")
            exit(1)

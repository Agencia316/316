import os
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.user import User

load_dotenv()

ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")


def init_api():
    FacebookAdsApi.init(access_token=ACCESS_TOKEN)


def get_ad_accounts():
    me = User(fbid="me")
    accounts = me.get_ad_accounts(fields=[
        AdAccount.Field.id,
        AdAccount.Field.name,
        AdAccount.Field.account_status,
        AdAccount.Field.currency,
        AdAccount.Field.amount_spent,
    ])
    return list(accounts)


def get_campaigns(ad_account_id):
    account = AdAccount(ad_account_id)
    campaigns = account.get_campaigns(fields=[
        "id",
        "name",
        "status",
        "objective",
        "daily_budget",
        "lifetime_budget",
        "start_time",
        "stop_time",
    ])
    return list(campaigns)


def get_insights(ad_account_id, date_preset="last_7d"):
    account = AdAccount(ad_account_id)
    insights = account.get_insights(fields=[
        "impressions",
        "clicks",
        "spend",
        "ctr",
        "cpc",
        "reach",
        "actions",
    ], params={
        "date_preset": date_preset,
        "level": "account",
    })
    return list(insights)


if __name__ == "__main__":
    init_api()
    print("Conectado a API do Facebook com sucesso!\n")

    print("=== Contas de Anuncio ===")
    accounts = get_ad_accounts()
    for acc in accounts:
        print(f"ID: {acc['id']} | Nome: {acc.get('name', 'N/A')} | Status: {acc.get('account_status')} | Moeda: {acc.get('currency')}")

    if accounts:
        first_account_id = accounts[0]["id"]
        print(f"\n=== Campanhas da conta {first_account_id} ===")
        campaigns = get_campaigns(first_account_id)
        for c in campaigns:
            print(f"ID: {c['id']} | Nome: {c['name']} | Status: {c['status']} | Objetivo: {c.get('objective')}")

        print(f"\n=== Insights (ultimos 7 dias) da conta {first_account_id} ===")
        insights = get_insights(first_account_id)
        for insight in insights:
            print(f"Impressoes: {insight.get('impressions')} | Cliques: {insight.get('clicks')} | Gasto: {insight.get('spend')} | CTR: {insight.get('ctr')}")

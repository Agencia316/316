import os
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")


def get_client() -> ApifyClient:
    if not APIFY_API_TOKEN:
        raise ValueError("APIFY_API_TOKEN não definido no .env")
    return ApifyClient(APIFY_API_TOKEN)


def run_actor(actor_id: str, run_input: dict) -> list:
    client = get_client()
    run = client.actor(actor_id).call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    return items


def get_dataset_items(dataset_id: str) -> list:
    client = get_client()
    items = list(client.dataset(dataset_id).iterate_items())
    return items


if __name__ == "__main__":
    client = get_client()
    user = client.user("me").get()
    print("Conectado ao Apify com sucesso!")
    print(f"Usuário: {user.get('username')} | Plano: {user.get('plan', {}).get('id', 'N/A')}")

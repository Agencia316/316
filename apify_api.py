import os
from dotenv import load_dotenv

load_dotenv()

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
APIFY_MOCK = os.getenv("APIFY_MOCK", "false").lower() == "true"


class _MockUserClient:
    def get(self):
        return {
            "username": "agencia316_mock",
            "plan": {"id": "SCALE"},
            "email": "contato@316.com.br",
        }


class _MockActorClient:
    def call(self, run_input=None):
        return {"defaultDatasetId": "mock-dataset-id"}


class _MockDatasetClient:
    def iterate_items(self):
        return iter([
            {"title": "Mock Item 1", "url": "https://example.com/1"},
            {"title": "Mock Item 2", "url": "https://example.com/2"},
        ])


class _MockApifyClient:
    def user(self, user_id):
        return _MockUserClient()

    def actor(self, actor_id):
        return _MockActorClient()

    def dataset(self, dataset_id):
        return _MockDatasetClient()


def get_client():
    if APIFY_MOCK:
        return _MockApifyClient()
    from apify_client import ApifyClient
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
    mode = "[MOCK]" if APIFY_MOCK else "[REAL]"
    print(f"Conectado ao Apify com sucesso! {mode}")
    print(f"Usuário: {user.get('username')} | Plano: {user.get('plan', {}).get('id', 'N/A')}")

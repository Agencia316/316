import os
from dotenv import load_dotenv

load_dotenv()

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
APIFY_MOCK = os.getenv("APIFY_MOCK", "false").lower() == "true"

INSTAGRAM_SCRAPER_ACTOR = "apify/instagram-scraper"


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
            {
                "id": "mock_post_1",
                "type": "Image",
                "shortCode": "CxMockPost1",
                "caption": "Post de exemplo #mock #316",
                "likesCount": 1420,
                "commentsCount": 38,
                "timestamp": "2024-03-01T12:00:00.000Z",
                "url": "https://www.instagram.com/p/CxMockPost1/",
                "displayUrl": "https://example.com/img1.jpg",
                "ownerUsername": "perfil_mock",
            },
            {
                "id": "mock_post_2",
                "type": "Video",
                "shortCode": "CxMockPost2",
                "caption": "Vídeo de exemplo #reels",
                "likesCount": 3850,
                "commentsCount": 92,
                "videoViewCount": 21000,
                "timestamp": "2024-03-05T18:30:00.000Z",
                "url": "https://www.instagram.com/p/CxMockPost2/",
                "displayUrl": "https://example.com/img2.jpg",
                "ownerUsername": "perfil_mock",
            },
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


def scrape_instagram_posts(username: str, max_posts: int = 20) -> list:
    """Raspa posts de um perfil público do Instagram.

    Args:
        username: nome do perfil (sem @), ex: 'nike'
        max_posts: número máximo de posts a retornar

    Returns:
        Lista de dicts com campos: id, type, shortCode, caption,
        likesCount, commentsCount, timestamp, url, displayUrl, ownerUsername
    """
    run_input = {
        "directUrls": [f"https://www.instagram.com/{username}/"],
        "resultsType": "posts",
        "resultsLimit": max_posts,
        "addParentData": False,
    }
    return run_actor(INSTAGRAM_SCRAPER_ACTOR, run_input)


if __name__ == "__main__":
    import json

    client = get_client()
    user = client.user("me").get()
    mode = "[MOCK]" if APIFY_MOCK else "[REAL]"
    print(f"Conectado ao Apify com sucesso! {mode}")
    print(f"Usuário: {user.get('username')} | Plano: {user.get('plan', {}).get('id', 'N/A')}")

    print("\n=== Raspando posts do Instagram ===")
    username = input("Digite o @ do perfil (sem @): ").strip()
    posts = scrape_instagram_posts(username, max_posts=10)
    print(f"\n{len(posts)} posts encontrados:\n")
    for p in posts:
        print(f"[{p.get('type','?')}] {p.get('timestamp','')[:10]}  ❤ {p.get('likesCount',0)}  💬 {p.get('commentsCount',0)}")
        caption = (p.get('caption') or '')[:80]
        if caption:
            print(f"  {caption}")
        print(f"  {p.get('url','')}")
        print()

import os
import re
import requests
from pathlib import Path
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
                "displayUrl": "https://example.com/thumb2.jpg",
                "videoUrl": "https://example.com/video2.mp4",
                "ownerUsername": "perfil_mock",
            },
            {
                "id": "mock_post_3",
                "type": "Sidecar",
                "shortCode": "CxMockPost3",
                "caption": "Carrossel de exemplo",
                "likesCount": 980,
                "commentsCount": 15,
                "timestamp": "2024-03-10T09:00:00.000Z",
                "url": "https://www.instagram.com/p/CxMockPost3/",
                "displayUrl": "https://example.com/thumb3.jpg",
                "ownerUsername": "perfil_mock",
                "sidecarMedia": [
                    {"displayUrl": "https://example.com/slide1.jpg", "type": "Image"},
                    {"displayUrl": "https://example.com/slide2.jpg", "type": "Image"},
                    {"displayUrl": "https://example.com/slide3.jpg", "videoUrl": "https://example.com/slide3.mp4", "type": "Video"},
                ],
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
        likesCount, commentsCount, timestamp, url, displayUrl,
        videoUrl (se vídeo), sidecarMedia (se carrossel), ownerUsername
    """
    run_input = {
        "directUrls": [f"https://www.instagram.com/{username}/"],
        "resultsType": "posts",
        "resultsLimit": max_posts,
        "addParentData": False,
    }
    return run_actor(INSTAGRAM_SCRAPER_ACTOR, run_input)


def _sanitize(text: str) -> str:
    """Remove caracteres inválidos para nomes de arquivo."""
    return re.sub(r'[\\/*?:"<>|]', "_", text)


def _download_file(url: str, dest: Path) -> bool:
    """Faz download de uma URL para dest. Retorna True se bem-sucedido."""
    if APIFY_MOCK:
        dest.write_text(f"[MOCK] conteúdo simulado de {url}\n")
        return True
    try:
        resp = requests.get(url, stream=True, timeout=30)
        resp.raise_for_status()
        dest.write_bytes(resp.content)
        return True
    except requests.RequestException as e:
        print(f"  [ERRO] Falha ao baixar {url}: {e}")
        return False


def _ext_from_url(url: str, default: str = ".jpg") -> str:
    """Extrai extensão da URL (sem query string)."""
    path = url.split("?")[0]
    suffix = Path(path).suffix
    return suffix if suffix else default


def download_post_media(post: dict, output_dir: str = "instagram_downloads") -> list[Path]:
    """Baixa as mídias de um post (imagem, vídeo ou carrossel).

    Args:
        post: dict retornado por scrape_instagram_posts()
        output_dir: pasta de destino (criada automaticamente)

    Returns:
        Lista de Paths dos arquivos baixados.
    """
    base_dir = Path(output_dir)
    short_code = post.get("shortCode", post.get("id", "unknown"))
    post_dir = base_dir / _sanitize(short_code)
    post_dir.mkdir(parents=True, exist_ok=True)

    post_type = post.get("type", "Image")
    downloaded: list[Path] = []

    if post_type == "Sidecar":
        slides = post.get("sidecarMedia") or []
        for i, slide in enumerate(slides, start=1):
            if slide.get("type") == "Video" and slide.get("videoUrl"):
                url = slide["videoUrl"]
                ext = _ext_from_url(url, ".mp4")
                dest = post_dir / f"slide_{i:02d}{ext}"
            else:
                url = slide.get("displayUrl", "")
                ext = _ext_from_url(url, ".jpg")
                dest = post_dir / f"slide_{i:02d}{ext}"
            if url and _download_file(url, dest):
                downloaded.append(dest)

    elif post_type == "Video":
        video_url = post.get("videoUrl", "")
        if video_url:
            ext = _ext_from_url(video_url, ".mp4")
            dest = post_dir / f"video{ext}"
            if _download_file(video_url, dest):
                downloaded.append(dest)
        # thumbnail
        thumb_url = post.get("displayUrl", "")
        if thumb_url:
            ext = _ext_from_url(thumb_url, ".jpg")
            dest = post_dir / f"thumbnail{ext}"
            if _download_file(thumb_url, dest):
                downloaded.append(dest)

    else:  # Image
        img_url = post.get("displayUrl", "")
        if img_url:
            ext = _ext_from_url(img_url, ".jpg")
            dest = post_dir / f"image{ext}"
            if _download_file(img_url, dest):
                downloaded.append(dest)

    return downloaded


if __name__ == "__main__":
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
        post_type = p.get("type", "?")
        print(f"[{post_type}] {p.get('timestamp','')[:10]}  ❤ {p.get('likesCount',0)}  💬 {p.get('commentsCount',0)}")
        caption = (p.get("caption") or "")[:80]
        if caption:
            print(f"  {caption}")
        print(f"  {p.get('url','')}")

        files = download_post_media(p, output_dir="instagram_downloads")
        for f in files:
            print(f"  -> {f}")
        print()

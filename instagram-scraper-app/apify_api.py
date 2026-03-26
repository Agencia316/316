import re
import requests
from pathlib import Path


INSTAGRAM_SCRAPER_ACTOR = "apify/instagram-scraper"


def _get_client(api_token: str):
    from apify_client import ApifyClient
    return ApifyClient(api_token)


def run_actor(api_token: str, actor_id: str, run_input: dict) -> list:
    client = _get_client(api_token)
    run = client.actor(actor_id).call(run_input=run_input)
    return list(client.dataset(run["defaultDatasetId"]).iterate_items())


def scrape_instagram_posts(api_token: str, username: str, max_posts: int = 20) -> list:
    """Raspa posts de um perfil público do Instagram via Apify.

    Args:
        api_token: token da API do Apify
        username: nome do perfil (sem @)
        max_posts: número máximo de posts

    Returns:
        Lista de dicts com: id, type, shortCode, caption, likesCount,
        commentsCount, videoViewCount, timestamp, url, displayUrl,
        videoUrl, sidecarMedia, ownerUsername
    """
    run_input = {
        "directUrls": [f"https://www.instagram.com/{username}/"],
        "resultsType": "posts",
        "resultsLimit": max_posts,
        "addParentData": False,
    }
    return run_actor(api_token, INSTAGRAM_SCRAPER_ACTOR, run_input)


def _sanitize(text: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", text)


def _ext_from_url(url: str, default: str = ".jpg") -> str:
    path = url.split("?")[0]
    suffix = Path(path).suffix
    return suffix if suffix else default


def _download_file(url: str, dest: Path) -> bool:
    try:
        resp = requests.get(url, stream=True, timeout=30)
        resp.raise_for_status()
        dest.write_bytes(resp.content)
        return True
    except requests.RequestException as e:
        print(f"  [ERRO] {url}: {e}")
        return False


def download_post_media(post: dict, output_dir: str = "downloads") -> list[Path]:
    """Baixa as mídias de um post (imagem, vídeo ou carrossel).

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
        for i, slide in enumerate(post.get("sidecarMedia") or [], start=1):
            if slide.get("type") == "Video" and slide.get("videoUrl"):
                url = slide["videoUrl"]
                dest = post_dir / f"slide_{i:02d}{_ext_from_url(url, '.mp4')}"
            else:
                url = slide.get("displayUrl", "")
                dest = post_dir / f"slide_{i:02d}{_ext_from_url(url, '.jpg')}"
            if url and _download_file(url, dest):
                downloaded.append(dest)

    elif post_type == "Video":
        video_url = post.get("videoUrl", "")
        if video_url:
            dest = post_dir / f"video{_ext_from_url(video_url, '.mp4')}"
            if _download_file(video_url, dest):
                downloaded.append(dest)
        thumb_url = post.get("displayUrl", "")
        if thumb_url:
            dest = post_dir / f"thumbnail{_ext_from_url(thumb_url, '.jpg')}"
            if _download_file(thumb_url, dest):
                downloaded.append(dest)

    else:  # Image
        img_url = post.get("displayUrl", "")
        if img_url:
            dest = post_dir / f"image{_ext_from_url(img_url, '.jpg')}"
            if _download_file(img_url, dest):
                downloaded.append(dest)

    return downloaded

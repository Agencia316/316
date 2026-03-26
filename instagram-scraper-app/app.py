import streamlit as st
import pandas as pd
from apify_api import scrape_instagram_posts, download_post_media

st.set_page_config(
    page_title="Instagram Scraper",
    page_icon="📸",
    layout="wide",
)

# ── token via st.secrets ou input manual ──────────────────────────────────────
api_token = st.secrets.get("APIFY_API_TOKEN", "") if hasattr(st, "secrets") else ""

if not api_token:
    st.sidebar.warning("Token Apify não configurado em secrets.")
    api_token = st.sidebar.text_input("Apify API Token", type="password")

# ── sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.header("Configurações")
username = st.sidebar.text_input("Perfil (@)", placeholder="ex: nike")
max_posts = st.sidebar.slider("Máximo de posts", 1, 50, 12)
enable_download = st.sidebar.checkbox("Baixar mídias", value=False)
buscar = st.sidebar.button("Buscar posts", type="primary", use_container_width=True)

# ── header ────────────────────────────────────────────────────────────────────
st.title("📸 Instagram Scraper")
st.caption("Raspe posts públicos do Instagram via Apify e baixe imagens, vídeos e carrosséis.")

if not buscar:
    st.info("Configure o perfil na barra lateral e clique em **Buscar posts**.")
    st.stop()

if not api_token:
    st.error("Insira seu Apify API Token na barra lateral para continuar.")
    st.stop()

if not username.strip():
    st.warning("Digite um nome de perfil.")
    st.stop()

# ── busca ─────────────────────────────────────────────────────────────────────
with st.spinner(f"Buscando posts de @{username.strip()}..."):
    try:
        posts = scrape_instagram_posts(api_token, username.strip(), max_posts)
    except Exception as e:
        st.error(f"Erro ao buscar posts: {e}")
        st.stop()

if not posts:
    st.warning("Nenhum post encontrado. Verifique se o perfil é público e o nome está correto.")
    st.stop()

# ── métricas ──────────────────────────────────────────────────────────────────
total_likes = sum(p.get("likesCount") or 0 for p in posts)
total_comments = sum(p.get("commentsCount") or 0 for p in posts)
total_views = sum(p.get("videoViewCount") or 0 for p in posts)
avg_likes = total_likes // len(posts)

st.success(f"**{len(posts)} posts** encontrados para @{username.strip()}")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Posts", len(posts))
c2.metric("Total curtidas", f"{total_likes:,}")
c3.metric("Média curtidas", f"{avg_likes:,}")
c4.metric("Views (vídeos)", f"{total_views:,}" if total_views else "—")

st.divider()

# ── grade de posts ────────────────────────────────────────────────────────────
TYPE_BADGE = {
    "Image": "🖼️ Imagem",
    "Video": "🎬 Vídeo",
    "Sidecar": "🎠 Carrossel",
}

COLS = 3
for row_start in range(0, len(posts), COLS):
    cols = st.columns(COLS)
    for col, post in zip(cols, posts[row_start: row_start + COLS]):
        with col:
            post_type = post.get("type", "Image")
            slides = post.get("sidecarMedia") or []
            badge = TYPE_BADGE.get(post_type, post_type)
            if post_type == "Sidecar":
                badge += f" ({len(slides)})"

            date = (post.get("timestamp") or "")[:10]
            likes = post.get("likesCount") or 0
            comments = post.get("commentsCount") or 0
            views = post.get("videoViewCount")
            caption = (post.get("caption") or "").strip()
            thumb = post.get("displayUrl", "")
            post_url = post.get("url", "")

            st.markdown(f"**{badge}** &nbsp;·&nbsp; {date}")

            if thumb:
                st.image(thumb, use_container_width=True)

            stats = f"❤️ {likes:,} &nbsp;&nbsp; 💬 {comments:,}"
            if views:
                stats += f" &nbsp;&nbsp; 👁️ {views:,}"
            st.markdown(stats)

            if caption:
                with st.expander("Legenda"):
                    st.write(caption)

            if post_url:
                st.markdown(f"[↗ Abrir no Instagram]({post_url})")

            if enable_download:
                files = download_post_media(post, output_dir="downloads")
                if files:
                    with st.expander(f"📁 {len(files)} arquivo(s)"):
                        for f in files:
                            p = str(f)
                            st.code(p)
                            # preview inline para imagens
                            if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                                st.image(p, use_container_width=True)

            st.markdown("---")

# ── tabela ────────────────────────────────────────────────────────────────────
with st.expander("Tabela completa"):
    rows = [
        {
            "Tipo": p.get("type", ""),
            "Data": (p.get("timestamp") or "")[:10],
            "Curtidas": p.get("likesCount") or 0,
            "Comentários": p.get("commentsCount") or 0,
            "Views": p.get("videoViewCount") or 0,
            "Legenda": (p.get("caption") or "")[:120],
            "URL": p.get("url", ""),
        }
        for p in posts
    ]
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Baixar CSV", csv, "posts.csv", "text/csv")

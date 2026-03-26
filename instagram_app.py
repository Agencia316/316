import streamlit as st
from pathlib import Path
from apify_api import scrape_instagram_posts, download_post_media, APIFY_MOCK

st.set_page_config(
    page_title="316 — Instagram Scraper",
    page_icon="📸",
    layout="wide",
)

st.title("📸 Instagram Scraper")
if APIFY_MOCK:
    st.info("Modo MOCK ativo — dados simulados. Defina `APIFY_MOCK=false` no `.env` para usar dados reais.")

# ── sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Configurações")
    username = st.text_input("Perfil (@)", placeholder="ex: nike")
    max_posts = st.slider("Máximo de posts", 1, 50, 12)
    download = st.checkbox("Baixar mídias automaticamente", value=False)
    if download:
        output_dir = st.text_input("Pasta de destino", value="instagram_downloads")
    buscar = st.button("Buscar posts", type="primary", use_container_width=True)

# ── busca ─────────────────────────────────────────────────────────────────────
if buscar:
    if not username.strip():
        st.warning("Digite um nome de perfil.")
        st.stop()

    with st.spinner(f"Buscando posts de @{username}..."):
        try:
            posts = scrape_instagram_posts(username.strip(), max_posts=max_posts)
        except Exception as e:
            st.error(f"Erro ao buscar posts: {e}")
            st.stop()

    if not posts:
        st.warning("Nenhum post encontrado.")
        st.stop()

    st.success(f"{len(posts)} posts encontrados para **@{username}**")

    # métricas resumo
    total_likes = sum(p.get("likesCount") or 0 for p in posts)
    total_comments = sum(p.get("commentsCount") or 0 for p in posts)
    total_views = sum(p.get("videoViewCount") or 0 for p in posts)
    tipos = {p.get("type", "?") for p in posts}

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Posts", len(posts))
    c2.metric("Total curtidas", f"{total_likes:,}")
    c3.metric("Total comentários", f"{total_comments:,}")
    c4.metric("Views (vídeos)", f"{total_views:,}" if total_views else "—")

    st.divider()

    # grade de posts
    cols_per_row = 3
    for row_start in range(0, len(posts), cols_per_row):
        row_posts = posts[row_start: row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, post in zip(cols, row_posts):
            with col:
                post_type = post.get("type", "Image")
                short_code = post.get("shortCode", post.get("id", ""))
                post_url = post.get("url", "")
                thumb_url = post.get("displayUrl", "")
                caption = (post.get("caption") or "").strip()
                likes = post.get("likesCount") or 0
                comments = post.get("commentsCount") or 0
                views = post.get("videoViewCount")
                date = (post.get("timestamp") or "")[:10]
                slides = post.get("sidecarMedia") or []

                # tipo badge
                badge = {"Image": "🖼️ Imagem", "Video": "🎬 Vídeo", "Sidecar": f"🎠 Carrossel ({len(slides)} itens)"}.get(post_type, post_type)
                st.markdown(f"**{badge}** · {date}")

                if thumb_url and not APIFY_MOCK:
                    st.image(thumb_url, use_container_width=True)
                elif thumb_url:
                    st.caption(f"[thumb] {thumb_url}")

                st.markdown(f"❤️ {likes:,} &nbsp; 💬 {comments:,}" + (f" &nbsp; 👁️ {views:,}" if views else ""))

                if caption:
                    with st.expander("Ver legenda"):
                        st.write(caption)

                if post_url:
                    st.markdown(f"[Abrir no Instagram]({post_url})")

                # download
                if download:
                    with st.spinner("Baixando..."):
                        files = download_post_media(post, output_dir=output_dir)
                    if files:
                        with st.expander(f"📁 {len(files)} arquivo(s) baixado(s)"):
                            for f in files:
                                st.code(str(f))

                st.markdown("---")

    # tabela completa
    with st.expander("Ver todos os dados em tabela"):
        import pandas as pd
        rows = []
        for p in posts:
            rows.append({
                "Tipo": p.get("type", ""),
                "Data": (p.get("timestamp") or "")[:10],
                "Curtidas": p.get("likesCount") or 0,
                "Comentários": p.get("commentsCount") or 0,
                "Views": p.get("videoViewCount") or 0,
                "Legenda": (p.get("caption") or "")[:100],
                "URL": p.get("url", ""),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

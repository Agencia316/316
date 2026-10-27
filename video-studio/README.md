# video-studio — vídeos explicativos animados (estilo "@tatica.explicada")

Estúdio para gerar **vídeos verticais 1080×1920 (Reels/TikTok/Shorts)** com animação de infográfico:
campo tático com bolinhas, bonecos chapados, números gigantes, gráficos e títulos em duas linhas
(branco + amarelo). Serve para futebol, mas os componentes são genéricos — troque tema/cores e
funciona para qualquer assunto (negócios, história, ciência, marketing…).

## Rodar

```bash
cd video-studio
node engine/render.mjs episodes/exemplo-classico.js                 # -> out/exemplo-classico.mp4
node engine/render.mjs episodes/exemplo-classico.js --still 13      # só 1 frame (PNG) no segundo 13
node engine/render.mjs episodes/exemplo-classico.js --audio trilha.mp3   # com música/locução
# preview ao vivo: abra engine/stage.html?ep=episodes/exemplo-classico.js&play=1 no navegador
```
Requer Node 18+, `playwright` (Chromium) e `ffmpeg`. A fonte `fonts/Anton-Regular.ttf` (OFL) dá o visual condensado dos títulos.
Render: ~2 s de render por segundo de vídeo.

## O que os 3 vídeos de referência têm em comum (a "gramática")

| Elemento | Como é | Onde está no código |
|---|---|---|
| Formato | 1080×1920, 30fps, 73–78 s, com áudio (trilha + efeitos) | `render.mjs` |
| Visual | fundo quase preto (#0b0b10), texto off-white, **amarelo #f5b81c** como único acento, roxo/branco para os dois times | `engine.js` → `T` |
| Título | "kicker" minúsculo em mono (• O CENÁRIO) + 2 linhas em fonte condensada: 1ª branca, 2ª amarela; entram em *stagger* subindo + fade | `C.title` |
| Estrutura | gancho → cenário → plano/tática → lance-chave → consequência → número-prova → **pergunta + "COMENTA AÍ / SEGUE"** | `episodes/*.js` |
| Cenas | 4–7 s cada, fade curto entre elas, **cada cena = 1 ideia = 1 título novo** | `scenes[]` |
| Campo tático | vista de cima, linhas finas translúcidas, 11 + 11 bolinhas, formação em 4-3-3 / 4-4-2; bloco de jogadores se move, zona tracejada amarela ("REAL COMPACTO"), anel pulsante no protagonista, etiqueta com nome | `C.pitch`, `C.dot`, `C.zone`, `Formations` |
| Setas | amarela = passe/bola; verde = corrida (sólida = principal, tracejada = secundária); desenham-se progressivamente | `C.arrow` |
| Placar HUD | "BAR 0 x 0 RMA" + selo amarelo do minuto, canto superior direito | `C.score` |
| Bonecos | personagens chapados (cabeça oval, camisa, calção, meias), poses: braços cruzados, braços para cima, mãos na cabeça, com bola; etiqueta acima | `C.figure`, `C.kits` |
| Número-prova | boneco + número amarelo gigante contando de 0 até o valor + legenda | `C.bigNumber` |
| Gráfico | barras simples, uma cinza (referência) e uma amarela (protagonista) | `C.bars` |
| Fecho | "FOI JUSTO?" / "POSSE GANHA JOGO?" + dois personagens com **VS** + CTA "COMENTA AÍ" | `C.cta` |
| Marca | @perfil no topo + ícone Instagram/@ no rodapé o tempo todo | `C.chrome` |

Os 3 episódios analisados: (1) Barça 1×2 Real — "o Barça teve a bola, o Mourinho teve o jogo";
(2) Harry Kane Bola de Ouro 2026 — "de pé-frio a melhor do mundo" (números: 0 títulos → 73 gols → 3 títulos → 33 anos);
(3) Flamengo × Estudiantes — "180 minutos, 0 gols; quem decide é o goleiro". Todos seguem o mesmo molde:
**tese em 1 frase → 5–6 cenas de evidência visual → pergunta aberta para gerar comentário.**

## Como criar um vídeo novo (qualquer tema)

1. Copie `episodes/exemplo-classico.js` para `episodes/meu-tema.js`.
2. Escreva o roteiro como lista de cenas: `{ dur: 5, draw: (t, api) => string SVG }`.
   `t` = segundos desde o início da cena; use `api.prog(t, inicio, duração, easing)` para animar
   qualquer coisa (posição, opacidade, contagem). Tudo é função de `t` → renderização determinística.
3. Combine componentes: `C.title(...) + C.pitch().svg + C.dot(...) + C.arrow(...) + C.figure(...) + C.bigNumber(...)`.
4. Veja um frame: `node engine/render.mjs episodes/meu-tema.js --still 12`, ajuste, depois renderize.
5. Para outro assunto sem campo: troque `C.pitch` por seu próprio fundo (linha do tempo, mapa, tabela)
   e `C.kits` por outros personagens; título, números, barras e CTA continuam iguais.

Receita de roteiro (≈ 70 s): gancho 4 s · cenário 5 s · plano 6 s · lance 6 s · reação 5 s ·
número-prova 5 s · gráfico 5 s · (repita 2–3 evidências) · pergunta+CTA 6 s.

## Próximos passos sugeridos
- Áudio: trilha + whoosh/hit nas trocas de cena (ffmpeg `amix`), ou locução (TTS) alinhada por cena.
- Mais poses/personagens (chutando, comemorando, goleiro caindo) e cena "gol" com trave (vista lateral).
- Pipeline de dados: ler JSON (placar, minutos, posições) e gerar as cenas automaticamente.

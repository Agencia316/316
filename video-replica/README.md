# Stick explainer (réplica do formato)

Vídeo 1080x1920 / 30fps gerado por código: boneco de palitos, headline/stickers, legenda karaokê, transição de blur entre capítulos, contador animado e end card.

- `script.js` – **edite aqui** o roteiro (chip, headline, ícones, pose, legenda; `*palavra*` = destaque).
- `index.html` – motor de animação (canvas, função pura do tempo).
- `render.js` – renderiza frame a frame com Playwright e junta com ffmpeg.

```
node render.js                  # -> out/video.mp4 (~7 min)
node render.js --still 5,12.5   # PNGs de teste rápidos em out/
```

Ícones disponíveis: receipt, check, heart, bag, phone, house, calendar, magnifier, trophy.
Poses: idle, wave, point, up, shrug, hold, hands. Rostos: happy, angry, surprised, smirk. Acessórios: crown, horns.
O vídeo sai sem narração (faixa de áudio silenciosa); grave/gere a voz e troque o `anullsrc` no `render.js`.

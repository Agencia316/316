# ⚽ 7 a 0 — Monte sua Seleção dos Sonhos

Recriação (projeto de estudo) do conceito do jogo [7a0.com.br](https://7a0.com.br):
você é o técnico, escolhe um esquema tático e monta a seleção dos sonhos
selecionando craques de todas as eras do futebol. O objetivo é ganhar de **7 a 0**.

## Como jogar

1. **Escolha o modo:**
   - **Clássico** — você vê o *overall* (força) de cada jogador.
   - **Almanaque** — o overall fica escondido; você escala de memória.
2. **Escolha o esquema tático:** 3-4-3, 4-3-3, 4-4-2, 3-5-2, 4-2-3-1 ou 5-3-2.
3. **Escale os 11:** para cada posição, o jogo sorteia alguns craques compatíveis.
   Escolha um para cada vaga (cada craque só pode ser usado uma vez).
4. **Finalize:** o overall médio do time define o placar — quanto melhor o
   elenco, maior a goleada. Será que dá pra cravar o 7 a 0?

## Como rodar

É um app 100% estático (HTML + CSS + JavaScript puro, sem dependências).
Basta abrir o arquivo no navegador:

```bash
# abrir direto
open 7a0/index.html          # macOS
xdg-open 7a0/index.html      # Linux

# ou servir localmente
cd 7a0 && python3 -m http.server 8000
# acesse http://localhost:8000
```

## Estrutura

| Arquivo          | Descrição                                              |
|------------------|--------------------------------------------------------|
| `index.html`     | Telas (início, jogo, resultado) e layout               |
| `styles.css`     | Estilo: campo, cards, animações                        |
| `players.js`     | Base de craques (nome, posição, overall, país, era)    |
| `formations.js`  | Coordenadas das posições de cada esquema tático         |
| `game.js`        | Lógica do jogo: draft, escalação e cálculo do resultado |

## Como adicionar jogadores

Edite `players.js` e inclua um objeto na lista `PLAYERS`:

```js
{ name: "Nome",  cat: "MID", ovr: 90, flag: "🇧🇷", era: "2000–10" }
```

`cat` pode ser `GK` (goleiro), `DEF` (defensor), `MID` (meio-campo) ou `FWD` (ataque).

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

## Base de jogadores

`players.js` é **gerado** por `build_players.py` e contém **mais de 6.000 jogadores
reais** de todas as Copas do Mundo de **1970 a 2022** (nome, posição, seleção,
edições e overall). Cada objeto tem o formato:

```js
{ name: "Lionel Messi", cat: "FWD", ovr: 96, flag: "🇦🇷", nat: "Argentina", era: "2010–2022" }
```

`cat`: `GK` (goleiro), `DEF` (defensor), `MID` (meio-campo) ou `FWD` (ataque).

### Fontes dos dados (domínio público)

- **1970–2014:** [`wikiscript/football.json`](https://github.com/wikiscript/football.json) — elencos da Wikipédia (inclui *caps*, jogos pela seleção).
- **2018, 2022:** [`openfootball/world-cup`](https://github.com/openfootball/world-cup).

### Sobre o "score" (overall)

Não existe um rating oficial válido para jogadores de todas as eras, então o
`ovr` é uma **estimativa derivada**, calculada em `build_players.py`:

- base por posição;
- **jogos pela seleção (caps)** — dado real, principal diferenciador;
- bônus por disputar **várias Copas** (durabilidade);
- ajuste curado para **lendas reconhecidas** (faixa 91–99);
- demais jogadores têm teto 90.

Para regenerar a base (precisa clonar as duas fontes em `/tmp`):

```bash
python3 build_players.py   # reescreve players.js
```

# ⚽ 7 a 0 — Monte sua Seleção dos Sonhos

Recriação (projeto de estudo) do conceito do jogo [7a0.com.br](https://7a0.com.br):
você é o técnico, escolhe um esquema tático e monta a seleção dos sonhos
selecionando craques de todas as eras do futebol. O objetivo é ganhar de **7 a 0**.

## Como jogar (igual ao 7a0 original)

1. **Escolha o modo:**
   - **Clássico** — você vê o *overall* (força) de cada jogador.
   - **Almanaque** — o overall fica escondido; você escala de memória.
2. **Escolha o esquema tático:** 3-4-3, 4-3-3, 4-4-2, 3-5-2, 4-2-3-1 ou 5-3-2.
3. **Monte os 11:** o jogo **sorteia uma seleção + uma Copa** (ex.: *Brasil 1970*) e
   mostra aquele elenco real. Escolha um jogador para preencher uma vaga em aberto.
   - **🎲 Trocar seleção / Copa** sorteia outra seleção, caso não goste da atual.
   - Clique num jogador já no campo para **trocá-lo** (a posição reabre e um novo
     elenco é sorteado).
   - Cada jogador só pode entrar uma vez.
4. **Finalize:** o overall médio do time define o placar — quanto melhor a
   escalação, maior a goleada. Será que dá pra cravar o 7 a 0?

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
| `index.html`     | Telas (início, jogo, resultado) e layout                |
| `styles.css`     | Estilo: campo, cards, animações                         |
| `squads.js`      | **Elencos** reais (seleção × Copa) — base usada pelo jogo |
| `players.js`     | Lista achatada de jogadores (auxiliar; não usada pelo jogo) |
| `formations.js`  | Coordenadas das posições de cada esquema tático          |
| `game.js`        | Lógica: sorteio de seleção/Copa, escalação e resultado   |
| `7a0-completo.html` | Versão single-file (tudo embutido), gerada por `build_standalone.py` |

## Base de jogadores

`squads.js` é **gerado** por `build_players.py` e preserva os **elencos reais**
(cada seleção de cada Copa, 1970–2022) — é a base que o jogo sorteia. Formato:

```js
{ team: "Argentina", year: 2022, flag: "🇦🇷",
  players: [ { n: "Lionel Messi", c: "FWD", o: 96 }, /* ... */ ] }
```

`c`: `GK` (goleiro), `DEF` (defensor), `MID` (meio-campo) ou `FWD` (ataque);
`o`: overall. São **368 elencos / 8.381 jogadores** de 14 Copas (1970 a 2022).

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

> **2026:** o 7a0 original anuncia ir até 2026, mas os convocados da Copa de 2026
> ainda não existem como dado aberto utilizável (a Copa é em jun/jul 2026 e as
> listas só saem na véspera). O `build_players.py` está pronto para incluí-la
> assim que houver uma fonte estática.

Para regenerar a base (precisa clonar as duas fontes em `/tmp`):

```bash
python3 build_players.py     # reescreve squads.js (e players.js)
python3 build_standalone.py  # reembrulha o 7a0-completo.html
```

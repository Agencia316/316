// Roteiro editável. Cada "beat" é um trecho de ~1.5–2.5s.
// cap: legenda karaokê (*palavra* = destaque laranja)
// head: {t: texto, c: 'black'|'orange', k: 'plain'|'sticker-orange'|'sticker-yellow', counter:{from,to,suffix,prefix}}
// props: [{i: ícone, x, y, s}]  (x,y em px no canvas 1080x1920; s = escala)
// pose: idle|wave|point|up|shrug|hold|hands   face: happy|angry|surprised|smirk   acc: none|crown|horns
// bubble: texto do balão de fala
window.SCRIPT = {
  brand: { name: "Willian Sonsin Oliveira", handle: "@williansonsinoliveira", top: "WILLIAN SONSIN" },
  disclaimer: "Conteúdo educativo. Consulte um contador.",
  endDur: 2.0,
  beats: [
    { d: 3.03, chip: "COMO PAGAR MENOS", head: { t: "COMO PAGAR MENOS IMPOSTO", c: "black" }, pose: "wave", face: "happy", cap: "Como pagar *MENOS* imposto," },
    { d: 1.5, chip: "COMO PAGAR MENOS", head: { t: "COMO PAGAR MENOS IMPOSTO", c: "black" }, props: [{ i: "receipt", x: 760, y: 900, s: 1 }, { i: "check", x: 800, y: 1010, s: 1 }], pose: "point", face: "smirk", cap: "dentro da *lei*." },
    { d: 2.68, chip: "COMO PAGAR MENOS", head: { t: "100% LEGAL", k: "sticker-orange" }, props: [{ i: "check", x: 780, y: 930, s: 1.4 }], pose: "up", face: "happy", cap: "Sem pegadinha e sem *risco*." },
    { d: 1.6, chip: "COMO PAGAR MENOS", head: { t: "SALVA ESSE VÍDEO", k: "sticker-yellow" }, props: [{ i: "phone", x: 780, y: 930, s: 1 }], pose: "hold", face: "smirk", cap: "Aqui vão *4 dicas* que" },
    { d: 3.05, chip: "COMO PAGAR MENOS", head: { t: "SALVA ESSE VÍDEO", k: "sticker-yellow" }, props: [{ i: "phone", x: 780, y: 930, s: 1 }], pose: "point", face: "happy", cap: "todo contribuinte deveria *conhecer*." },

    { d: 3.49, chip: "DICA 1 · PREVIDÊNCIA", head: { t: "PGBL ABATE O IR", k: "sticker-orange" }, props: [{ i: "bag", x: 780, y: 930, s: 1.1 }], pose: "idle", face: "happy", cap: "A primeira é *previdência privada*." },
    { d: 3.62, chip: "DICA 1 · PREVIDÊNCIA", head: { t: "ATÉ 12%", c: "orange" }, props: [{ i: "bag", x: 780, y: 930, s: 1.1 }, { i: "receipt", x: 900, y: 930, s: 0.9 }], pose: "point", face: "surprised", cap: "No modelo completo, o *PGBL* deixa" },
    { d: 2.47, chip: "DICA 1 · PREVIDÊNCIA", head: { t: "ATÉ 12%", c: "orange" }, props: [{ i: "calendar", x: 780, y: 930, s: 1.1 }], pose: "shrug", face: "happy", cap: "abater até *12%* da renda bruta." },

    { d: 3.11, chip: "DICA 2 · SAÚDE", head: { t: "GASTO MÉDICO ABATE", k: "sticker-orange" }, props: [{ i: "heart", x: 780, y: 930, s: 1.3 }], pose: "idle", face: "happy", cap: "A segunda são *despesas médicas*." },
    { d: 3.11, chip: "DICA 2 · SAÚDE", head: { t: "SEM LIMITE", c: "black" }, props: [{ i: "heart", x: 780, y: 930, s: 1.3 }], pose: "up", face: "surprised", cap: "Elas são dedutíveis *sem limite*," },
    { d: 2.76, chip: "DICA 2 · SAÚDE", head: { t: "SEM LIMITE", c: "black" }, props: [{ i: "receipt", x: 780, y: 900, s: 1.1 }, { i: "check", x: 830, y: 1010, s: 1 }], pose: "point", face: "smirk", cap: "desde que tenha *nota fiscal*." },

    { d: 2.48, chip: "DICA 3 · DEPENDENTES", head: { t: "DEPENDENTES", c: "black" }, props: [{ i: "house", x: 780, y: 930, s: 1.1 }], pose: "idle", face: "happy", cap: "A terceira: *dependentes*." },
    { d: 4.31, chip: "DICA 3 · DEPENDENTES", head: { t: "DEPENDENTES", c: "black" }, props: [{ i: "house", x: 700, y: 930, s: 1.1 }, { i: "heart", x: 880, y: 930, s: 0.9 }], pose: "hands", face: "happy", cap: "Cada dependente declarado gera uma *dedução*" },
    { d: 1.48, chip: "DICA 3 · DEPENDENTES", head: { t: "DEPENDENTES", c: "black" }, props: [{ i: "receipt", x: 780, y: 900, s: 1.1 }, { i: "check", x: 830, y: 1010, s: 1 }], pose: "point", face: "smirk", cap: "no cálculo do *imposto*." },

    { d: 2.88, chip: "DICA 4 · CONTADOR", head: { t: "PLANEJE O ANO TODO", k: "sticker-yellow" }, props: [{ i: "calendar", x: 780, y: 930, s: 1.2 }], pose: "idle", face: "happy", cap: "E a quarta: *planejamento*." },
    { d: 3.53, chip: "DICA 4 · CONTADOR", head: { t: "REGIME CERTO", c: "orange" }, props: [{ i: "magnifier", x: 780, y: 930, s: 1.2 }], pose: "point", face: "surprised", cap: "Escolher o regime certo com um *contador*" },
    { d: 2.46, chip: "DICA 4 · CONTADOR", head: { t: "REGIME CERTO", c: "orange" }, props: [{ i: "calendar", x: 780, y: 930, s: 1.1 }, { i: "check", x: 880, y: 1010, s: 1 }], pose: "shrug", face: "smirk", cap: "muda tudo no *final do ano*." },

    { d: 2.36, chip: "BOM CONTRIBUINTE", head: { t: "BOM CIDADÃO", k: "sticker-yellow" }, props: [{ i: "trophy", x: 780, y: 930, s: 1.2 }], pose: "up", face: "happy", acc: "crown", cap: "Assim você paga o *justo*," },
    { d: 1.93, chip: "BOM CONTRIBUINTE", head: { t: "", c: "orange", counter: { from: 0, to: 100, suffix: "%" } }, props: [{ i: "receipt", x: 780, y: 900, s: 1.1 }, { i: "check", x: 830, y: 1010, s: 1.1 }], pose: "idle", face: "happy", acc: "crown", cap: "100% *dentro da lei*." },
    { d: 3.93, chip: "BOM CONTRIBUINTE", head: { t: "MARCA ELE AQUI!", c: "orange" }, props: [{ i: "heart", x: 850, y: 1040, s: 1 }], pose: "point", face: "smirk", bubble: "marca aquele amigo", cap: "Marca aquele amigo que *paga demais*." }
  ]
};

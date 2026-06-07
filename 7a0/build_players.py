#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera players.js a partir de elencos reais das Copas do Mundo (1970 em diante).

Fontes (domínio público / open data, baixadas via git no ambiente):
  - 1970–2014: wikiscript/football.json  (wikitexto da Wikipédia, com 'caps')
  - 2018, 2022: openfootball/world-cup    (formato texto próprio)

Como NÃO existe uma "nota" oficial de jogador válida para todas as eras,
o score é DERIVADO (estimativa transparente): base por posição + jogos pela
seleção (caps, dado real) + bônus por participar de várias Copas + ajuste
curado para lendas reconhecidas. Não é um rating oficial.
"""
import os, re, sys, unicodedata, hashlib, json

WIKI_DIR = "/tmp/fb.json/_source/squads/world-cup"
OF_DIR   = "/tmp/openfootball_world-cup/more"
WIKI_YEARS = [1950, 1954, 1958, 1962, 1966, 1970, 1974, 1978, 1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014]
OF_YEARS   = [2018, 2022]

POS_MAP = {"GK": "GK", "DF": "DEF", "MF": "MID", "FW": "FWD"}

# código {{fb|XXX}} -> nome da seleção
FB_CODE = {
    "ALG":"Algeria","ANG":"Angola","ARG":"Argentina","AUS":"Australia","AUT":"Austria",
    "BEL":"Belgium","BIH":"Bosnia and Herzegovina","BOL":"Bolivia","BRA":"Brazil",
    "BUL":"Bulgaria","CAN":"Canada","CHI":"Chile","CHN":"China PR","CIV":"Ivory Coast",
    "CMR":"Cameroon","COL":"Colombia","CRC":"Costa Rica","CRO":"Croatia","CZE":"Czech Republic",
    "TCH":"Czechoslovakia","DEN":"Denmark","ECU":"Ecuador","EGY":"Egypt","ENG":"England",
    "ESP":"Spain","FRA":"France","FRG":"West Germany","GDR":"East Germany","GER":"Germany",
    "GHA":"Ghana","GRE":"Greece","HAI":"Haiti","HON":"Honduras","HUN":"Hungary","IRL":"Republic of Ireland",
    "IRN":"Iran","IRQ":"Iraq","ISL":"Iceland","ISR":"Israel","ITA":"Italy","JAM":"Jamaica",
    "JPN":"Japan","KSA":"Saudi Arabia","KOR":"South Korea","PRK":"Korea DPR","KUW":"Kuwait",
    "MAR":"Morocco","MEX":"Mexico","NED":"Netherlands","NGA":"Nigeria","NIR":"Northern Ireland",
    "NOR":"Norway","NZL":"New Zealand","PAN":"Panama","PAR":"Paraguay","PER":"Peru","POL":"Poland",
    "POR":"Portugal","QAT":"Qatar","ROU":"Romania","RSA":"South Africa","RUS":"Russia",
    "SCO":"Scotland","SEN":"Senegal","SRB":"Serbia","SCG":"Serbia and Montenegro","SVK":"Slovakia",
    "SVN":"Slovenia","SLV":"El Salvador","SUI":"Switzerland","SWE":"Sweden","TOG":"Togo",
    "TRI":"Trinidad and Tobago","TUN":"Tunisia","TUR":"Turkey","UAE":"United Arab Emirates",
    "UKR":"Ukraine","URS":"Soviet Union","URU":"Uruguay","USA":"United States","WAL":"Wales",
    "YUG":"Yugoslavia","ZAI":"Zaire",
}

# normalização de nomes de seleção (variações -> forma canônica)
NATION_ALIAS = {
    "Korea Republic":"South Korea","United States":"USA","Côte d'Ivoire":"Ivory Coast",
    "FR Yugoslavia":"Yugoslavia","SFR Yugoslavia":"Yugoslavia","China PR":"China",
}

# seleção -> bandeira emoji (defuntas usam aproximação; o nome também é exibido)
FLAG = {
    "Algeria":"🇩🇿","Angola":"🇦🇴","Argentina":"🇦🇷","Australia":"🇦🇺","Austria":"🇦🇹",
    "Belgium":"🇧🇪","Bolivia":"🇧🇴","Bosnia and Herzegovina":"🇧🇦","Brazil":"🇧🇷","Bulgaria":"🇧🇬",
    "Cameroon":"🇨🇲","Canada":"🇨🇦","Chile":"🇨🇱","China":"🇨🇳","Colombia":"🇨🇴","Costa Rica":"🇨🇷",
    "Croatia":"🇭🇷","Czech Republic":"🇨🇿","Czechoslovakia":"🇨🇿","Denmark":"🇩🇰","East Germany":"🇩🇪",
    "Ecuador":"🇪🇨","Egypt":"🇪🇬","El Salvador":"🇸🇻","England":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","France":"🇫🇷","Germany":"🇩🇪",
    "Ghana":"🇬🇭","Greece":"🇬🇷","Haiti":"🇭🇹","Honduras":"🇭🇳","Hungary":"🇭🇺","Iceland":"🇮🇸",
    "Iran":"🇮🇷","Iraq":"🇮🇶","Israel":"🇮🇱","Italy":"🇮🇹","Ivory Coast":"🇨🇮","Jamaica":"🇯🇲",
    "Japan":"🇯🇵","Korea DPR":"🇰🇵","Kuwait":"🇰🇼","Mexico":"🇲🇽","Morocco":"🇲🇦","Netherlands":"🇳🇱",
    "New Zealand":"🇳🇿","Nigeria":"🇳🇬","Northern Ireland":"🏴","Norway":"🇳🇴","Panama":"🇵🇦",
    "Paraguay":"🇵🇾","Peru":"🇵🇪","Poland":"🇵🇱","Portugal":"🇵🇹","Qatar":"🇶🇦","Republic of Ireland":"🇮🇪",
    "Romania":"🇷🇴","Russia":"🇷🇺","Saudi Arabia":"🇸🇦","Scotland":"🏴󠁧󠁢󠁳󠁣󠁴󠁿","Senegal":"🇸🇳",
    "Serbia":"🇷🇸","Serbia and Montenegro":"🇷🇸","Slovakia":"🇸🇰","Slovenia":"🇸🇮","South Africa":"🇿🇦",
    "South Korea":"🇰🇷","Soviet Union":"🇷🇺","Spain":"🇪🇸","Sweden":"🇸🇪","Switzerland":"🇨🇭",
    "Togo":"🇹🇬","Trinidad and Tobago":"🇹🇹","Tunisia":"🇹🇳","Turkey":"🇹🇷","Ukraine":"🇺🇦",
    "United Arab Emirates":"🇦🇪","Uruguay":"🇺🇾","USA":"🇺🇸","Wales":"🏴󠁧󠁢󠁷󠁬󠁳󠁿","West Germany":"🇩🇪",
    "Yugoslavia":"🇷🇸","Zaire":"🇨🇩",
}

# Ajuste curado de lendas: piso de score (nome canônico minúsculo, sem acento)
LEGENDS = {
    "pele":97,"diego maradona":96,"lionel messi":96,"cristiano ronaldo":95,
    "ronaldo":95,"johan cruyff":95,"franz beckenbauer":94,"zinedine zidane":94,
    "garrincha":93,"michel platini":92,"romario":92,"ronaldinho":92,"ronaldinho gaucho":92,
    "paolo maldini":92,"gerd muller":92,"marco van basten":92,"eusebio":92,"ferenc puskas":92,
    "alfredo di stefano":92,"kylian mbappe":92,"neymar":91,"andres iniesta":91,"xavi":91,
    "kaka":90,"rivaldo":91,"thierry henry":91,"roberto carlos":90,"cafu":90,"luis suarez":89,
    "iker casillas":91,"gianluigi buffon":92,"manuel neuer":91,"oliver kahn":90,"lev yashin":91,
    "fabio cannavaro":90,"andrea pirlo":90,"luka modric":90,"sergio ramos":90,"carles puyol":88,
    "philipp lahm":89,"bastian schweinsteiger":88,"toni kroos":89,"robert lewandowski":90,
    "wayne rooney":88,"david beckham":88,"steven gerrard":88,"frank lampard":87,
    "didier drogba":88,"samuel eto'o":88,"george weah":88,"hristo stoichkov":89,
    "gabriel batistuta":89,"juan roman riquelme":88,"hernan crespo":86,"diego forlan":86,
    "socrates":89,"zico":91,"falcao":87,"careca":85,"bebeto":86,"taffarel":85,"dunga":84,
    "rivelino":88,"jairzinho":88,"carlos alberto":88,"gerson":87,"tostao":87,"clodoaldo":83,
    "dida":85,"thiago silva":87,"marcelo":86,"dani alves":86,"kaka":90,"adriano":85,
    "michael ballack":88,"miroslav klose":88,"jurgen klinsmann":88,"lothar matthaus":90,
    "rudi voller":86,"karl-heinz rummenigge":89,"paul breitner":87,"gennaro gattuso":85,
    "francesco totti":89,"alessandro del piero":89,"roberto baggio":90,"franco baresi":90,
    "marco tardelli":85,"dino zoff":89,"gaetano scirea":86,"raul":88,"fernando torres":86,
    "fernando hierro":86,"luis figo":90,"deco":87,"rui costa":86,"pavel nedved":88,
    "patrick vieira":88,"didier deschamps":85,"laurent blanc":85,"fabien barthez":85,
    "marcel desailly":86,"lilian thuram":86,"hugo sanchez":86,"rafael marquez":84,
    "gheorghe hagi":89,"davor suker":87,"zvonimir boban":86,"robert prosinecki":85,
    "andriy shevchenko":89,"pavel ...":80,"jan ceulemans":84,"jean-marie pfaff":85,
    "ruud gullit":90,"frank rijkaard":88,"dennis bergkamp":89,"clarence seedorf":86,
    "edwin van der sar":87,"arjen robben":89,"wesley sneijder":88,"robin van persie":87,
    "ruud van nistelrooy":87,"patrick kluivert":86,"michael laudrup":88,"peter schmeichel":89,
    "gary lineker":87,"bobby moore":89,"gordon banks":89,"kevin keegan":86,
    "kenny dalglish":87,"mario kempes":88,"daniel passarella":87,"ossie ardiles":85,
    "teofilo cubillas":87,"elias figueroa":86,"carlos valderrama":87,"rene higuita":84,
    "faryd mondragon":80,"jay-jay okocha":86,"nwankwo kanu":85,"rashidi yekini":84,
    "roger milla":86,"abedi pele":86,"hidetoshi nakata":85,"park ji-sung":85,
    "harry kane":89,"raheem sterling":85,"jordan henderson":83,"kevin de bruyne":91,
    "eden hazard":89,"romelu lukaku":85,"vincent kompany":86,"thibaut courtois":89,
    "antoine griezmann":89,"paul pogba":87,"ngolo kante":88,"hugo lloris":86,"raphael varane":87,
    "karim benzema":89,"olivier giroud":84,"sadio mane":87,"kalidou koulibaly":85,
    "edinson cavani":87,"luis suarez":89,"diego godin":86,"james rodriguez":86,
    "radamel falcao":86,"alexis sanchez":85,"arturo vidal":86,"claudio bravo":84,
    "son heung-min":87,"takumi minamino":80,"achraf hakimi":85,"hakim ziyech":83,
    "vinicius junior":88,"casemiro":86,"alisson":88,"ederson":86,"richarlison":83,
    "joshua kimmich":87,"thomas muller":87,"ilkay gundogan":85,"leroy sane":85,
    "lautaro martinez":85,"angel di maria":87,"emiliano martinez":85,"rodrigo de paul":84,
    "bruno fernandes":87,"bernardo silva":87,"joao felix":83,"ruben dias":86,"pepe":86,
    "modric":90,"ivan rakitic":87,"mario mandzukic":85,"dejan lovren":82,
    "virgil van dijk":89,"frenkie de jong":86,"memphis depay":84,"matthijs de ligt":84,
}

def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def canon(name):
    return strip_accents(name).lower().strip()

# ---------- parsing wikiscript (1970-2014) ----------
def parse_nation_header(raw):
    """Resolve o nome da seleção a partir das variações de cabeçalho '===...==='."""
    h = raw.strip().strip("=").strip()
    # ignora seções estatísticas
    low = h.lower()
    if any(k in low for k in ("representation", "average age", "coaches")):
        return None
    m = re.search(r"\{\{fb\|([A-Z]{2,3})", h)
    if m:
        return FB_CODE.get(m.group(1))
    m = re.search(r"\[\[[^\]|]*\|([^\]]+)\]\]", h)  # [[X team|Name]]
    if m:
        return m.group(1).strip()
    m = re.search(r"\{\{flagicon\|([^}|]+)", h)
    if m:
        return m.group(1).strip()
    if re.match(r"^[A-Za-zÀ-ÿ .'()-]+$", h):
        return h
    return None

PLAYER_RE = re.compile(r"\{\{nat fs player\|(.*)$")
def extract_name(field):
    m = re.search(r"\[\[([^\]]+)\]\]", field)
    if not m:
        return None
    inner = m.group(1)
    name = inner.split("|")[-1] if "|" in inner else inner
    return name.strip()

def parse_wiki(path, year, records):
    nation = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s.startswith("===") and not s.startswith("===="):
                nation = parse_nation_header(s)
                continue
            if "nat fs player" not in s and "National football squad player" not in s:
                continue
            if nation is None:
                continue
            fields = dict()
            for part in s.split("|"):
                if "=" in part:
                    k, _, v = part.partition("=")
                    fields[k.strip()] = v.strip()
            pos = POS_MAP.get(fields.get("pos", "").upper()[:2])
            nm = extract_name("|".join(p for p in s.split("|") if p.strip().startswith("name=")) or "")
            if not nm:
                m = re.search(r"name=\s*\[\[([^\]]+)\]\]", s)
                nm = (m.group(1).split("|")[-1].strip() if m else None)
            if not nm or not pos:
                continue
            caps_raw = fields.get("caps", "")
            caps = int(caps_raw) if caps_raw.isdigit() else None
            records.append({"name": nm, "nation": nation, "pos": pos, "caps": caps, "year": year})

# ---------- parsing openfootball (2018, 2022) ----------
def titlecase(name):
    return " ".join(w if (w.isupper() and len(w) <= 3 and not w.isalpha()) else w.capitalize()
                     for w in name.split())

def parse_of(path, year, records):
    nation = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            s = line.rstrip("\n")
            t = s.strip()
            if t.startswith("=="):
                nation = t.strip("=").split("#")[0].strip()
                continue
            if not nation or "," not in t:
                continue
            parts = [p.strip() for p in t.split(",")]
            if len(parts) < 3:
                continue
            no, name, pos = parts[0], parts[1], parts[2]
            pos = POS_MAP.get(pos.upper()[:2])
            if not pos or no == "-":   # '-' = comissão técnica
                continue
            records.append({"name": titlecase(name), "nation": nation, "pos": pos, "caps": None, "year": year})

# ---------- score derivado ----------
BASE = {"GK": 71, "DEF": 71, "MID": 72, "FWD": 73}
def compute_score(cat, caps, n_cups, name_c):
    score = BASE[cat]
    if caps:
        score += min(caps, 150) * 0.085        # até ~+12.7 (dado real)
    score += min(n_cups - 1, 4) * 1.3          # durabilidade: até +5.2
    # jitter determinístico p/ desempate (±1.4)
    h = int(hashlib.md5(name_c.encode()).hexdigest(), 16) % 1000 / 1000
    score += (h - 0.5) * 2.8
    score = round(score)
    if name_c in LEGENDS:                       # lendas curadas: 91–99
        return int(max(66, min(99, max(score, LEGENDS[name_c]))))
    return int(max(66, min(90, score)))         # demais: teto 90

def main():
    records = []
    for y in WIKI_YEARS:
        parse_wiki(os.path.join(WIKI_DIR, f"{y}_FIFA_World_Cup_squads.txt"), y, records)
    for y in OF_YEARS:
        parse_of(os.path.join(OF_DIR, f"{y}_squads.txt"), y, records)

    # normaliza nações
    for r in records:
        r["nation"] = NATION_ALIAS.get(r["nation"], r["nation"])

    # dedup por (nome canônico + nação) — mescla caps e Copas
    agg = {}
    for r in records:
        key = (canon(r["name"]), r["nation"])
        a = agg.get(key)
        if not a:
            agg[key] = {"name": r["name"], "nation": r["nation"], "pos": {}, "caps": r["caps"] or 0, "years": set()}
            a = agg[key]
        a["pos"][r["pos"]] = a["pos"].get(r["pos"], 0) + 1
        if r["caps"]:
            a["caps"] = max(a["caps"], r["caps"])
        a["years"].add(r["year"])

    players = []
    skipped_flag = set()
    for (name_c, nation), a in agg.items():
        cat = max(a["pos"].items(), key=lambda kv: kv[1])[0]
        years = sorted(a["years"])
        era = f"{years[0]}" if len(years) == 1 else f"{years[0]}–{years[-1]}"
        flag = FLAG.get(nation)
        if not flag:
            skipped_flag.add(nation); flag = "🏳️"
        ovr = compute_score(cat, a["caps"], len(years), name_c)
        players.append({"name": a["name"], "cat": cat, "ovr": ovr,
                        "flag": flag, "nat": nation, "era": era})

    players.sort(key=lambda p: (-p["ovr"], p["name"]))

    by_cat = {}
    for p in players:
        by_cat[p["cat"]] = by_cat.get(p["cat"], 0) + 1
    sys.stderr.write(f"Total: {len(players)} | por posição: {by_cat}\n")
    if skipped_flag:
        sys.stderr.write(f"Nações sem bandeira (usando 🏳️): {sorted(skipped_flag)}\n")

    out = "/home/user/316/7a0/players.js"
    with open(out, "w", encoding="utf-8") as f:
        f.write("/* GERADO por build_players.py — NÃO editar à mão.\n")
        f.write("   Elencos reais das Copas do Mundo de 1970 a 2022.\n")
        f.write("   Fontes: wikiscript/football.json (1970–2014) e openfootball/world-cup (2018–2022).\n")
        f.write("   'ovr' é um score DERIVADO (estimativa): base por posição + caps (jogos pela\n")
        f.write("   seleção) + bônus por múltiplas Copas + ajuste para lendas. Não é rating oficial.\n")
        f.write("   cat: GK (goleiro), DEF (defensor), MID (meio-campo), FWD (atacante). */\n")
        f.write(f"const PLAYERS = {json.dumps(players, ensure_ascii=False)};\n")
    sys.stderr.write(f"Escrito: {out}\n")

    # ---------- squads.js: elencos preservados (seleção + Copa) ----------
    # score canônico por jogador (mesmo overall em todas as Copas que disputou)
    score_map, disp_map = {}, {}
    for (name_c, nation), a in agg.items():
        cat = max(a["pos"].items(), key=lambda kv: kv[1])[0]
        score_map[(name_c, nation)] = compute_score(cat, a["caps"], len(a["years"]), name_c)

    # agrupa por (nação, ano), dedup jogador dentro do elenco
    squads = {}
    for r in records:
        nation, year = r["nation"], r["year"]
        key = (nation, year)
        sq = squads.setdefault(key, {})
        pc = canon(r["name"])
        if pc in sq:
            continue
        # nome de exibição mais completo visto p/ esse jogador
        cur = disp_map.get((pc, nation))
        if not cur or len(r["name"]) > len(cur):
            disp_map[(pc, nation)] = r["name"]
        sq[pc] = {"c": r["pos"], "raw": r["name"]}

    squad_list = []
    for (nation, year), sq in squads.items():
        flag = FLAG.get(nation, "🏳️")
        plist = []
        for pc, info in sq.items():
            name = disp_map.get((pc, nation), info["raw"])
            ovr = score_map.get((pc, nation), 70)
            plist.append({"n": name, "c": info["c"], "o": ovr})
        # ordena por posição (GK,DEF,MID,FWD) e overall desc
        order = {"GK": 0, "DEF": 1, "MID": 2, "FWD": 3}
        plist.sort(key=lambda p: (order[p["c"]], -p["o"], p["n"]))
        squad_list.append({"team": nation, "year": year, "flag": flag, "players": plist})

    squad_list.sort(key=lambda s: (s["year"], s["team"]))
    sys.stderr.write(f"Elencos (seleção×Copa): {len(squad_list)} | "
                     f"jogadores totais: {sum(len(s['players']) for s in squad_list)}\n")

    out2 = "/home/user/316/7a0/squads.js"
    with open(out2, "w", encoding="utf-8") as f:
        f.write("/* GERADO por build_players.py — NÃO editar à mão.\n")
        f.write("   Elencos reais das Copas do Mundo (1970–2022), preservando seleção × edição.\n")
        f.write("   Fontes: wikiscript/football.json (1970–2014) e openfootball/world-cup (2018–2022).\n")
        f.write("   Cada item: { team, year, flag, players:[{n:nome, c:posição, o:overall}] }.\n")
        f.write("   'o' (overall) é estimativa derivada (caps + Copas + ajuste de lendas), não oficial.\n")
        f.write("   c: GK (goleiro), DEF (defensor), MID (meio-campo), FWD (atacante). */\n")
        f.write(f"const SQUADS = {json.dumps(squad_list, ensure_ascii=False)};\n")
    sys.stderr.write(f"Escrito: {out2}\n")

if __name__ == "__main__":
    main()

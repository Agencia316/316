#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera 7a0-completo.html: um único arquivo HTML com CSS e JS embutidos,
que roda só abrindo no navegador (sem depender dos outros arquivos)."""
import re

html = open("index.html", encoding="utf-8").read()
css = open("styles.css", encoding="utf-8").read()
bundle = "\n".join(open(f, encoding="utf-8").read()
                   for f in ("squads.js", "formations.js", "game.js"))

html = re.sub(r'\s*<link rel="stylesheet" href="styles.css" />',
              "\n  <style>\n" + css + "\n  </style>", html)
html = re.sub(r'\s*<script src="squads.js"></script>\s*'
              r'<script src="formations.js"></script>\s*'
              r'<script src="game.js"></script>',
              "\n  <script>\n" + bundle + "\n  </script>", html)

open("7a0-completo.html", "w", encoding="utf-8").write(html)
print("Escrito: 7a0-completo.html")

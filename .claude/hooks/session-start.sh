#!/bin/bash
# Instala as dependencias do dashboard para que a sessao ja comece pronta.
set -euo pipefail

# Só roda em sessoes remotas (Claude Code na nuvem). Local continua usando run.sh.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"

venv=".venv"
hashes="$venv/.session-start.sha256"

# Reinstala só quando este script ou o requirements.txt mudam desde a ultima vez.
if ! sha256sum --check --status "$hashes" 2>/dev/null; then
  # Apaga os hashes antes, para que um install que falhe seja refeito na proxima sessao.
  rm -f "$hashes"

  [ -x "$venv/bin/python" ] || python3 -m venv "$venv"
  "$venv/bin/python" -m pip install --quiet --disable-pip-version-check -r requirements.txt

  sha256sum .claude/hooks/session-start.sh requirements.txt > "$hashes" || rm -f "$hashes"
fi

# Toda sessao precisa do venv no PATH (streamlit, python com as libs instaladas).
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  {
    echo "export VIRTUAL_ENV=\"$PWD/$venv\""
    echo "export PATH=\"$PWD/$venv/bin:\$PATH\""
  } >> "$CLAUDE_ENV_FILE"
fi

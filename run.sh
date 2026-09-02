#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
  python3 -m venv "$ROOT/.venv"
  "$ROOT/.venv/bin/pip" install -r "$ROOT/requirements.txt"
fi
exec "$ROOT/.venv/bin/python" -m vibe.main

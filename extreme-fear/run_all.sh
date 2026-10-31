#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
# the study's own venv if it exists; otherwise $PYTHON or python3
PY="${PYTHON:-$( [ -x venv/bin/python ] && echo venv/bin/python || echo python3 )}"
for s in scripts/[0-9][0-9]_*.py; do
  echo "== $s"
  "$PY" "$s"
done
# shared/ lives in the repo root (two levels up in the monorepo, one in the public repo)
SHARED="$PWD"; while [ ! -d "$SHARED/shared" ]; do SHARED="$(dirname "$SHARED")"; [ "$SHARED" = / ] && { echo "shared/ not found" >&2; exit 1; }; done
"$PY" "$SHARED/shared/check_numbers.py" .

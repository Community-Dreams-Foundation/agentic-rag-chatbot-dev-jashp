#!/usr/bin/env bash
set -euo pipefail

echo "== Proximal Energy Sanity Check =="

rm -rf artifacts
mkdir -p artifacts

# 1. SMART PYTHON SELECTION: Prioritize the active venv or local 'python'
if [[ -n "${VIRTUAL_ENV:-}" ]]; then
  # If a venv is active, use its internal python directly
  if [[ -f "$VIRTUAL_ENV/Scripts/python.exe" ]]; then
    PY_CMD="$VIRTUAL_ENV/Scripts/python.exe" # Windows venv path
  else
    PY_CMD="$VIRTUAL_ENV/bin/python" # Unix venv path
  fi
else
  # Fallback for systems without an active venv
  PY_CMD=$(command -v python3 || command -v python)
fi

echo "Using Python: $PY_CMD"

# 2. RUN GENERATOR: Try 'make', otherwise use the PY_CMD we just found
if command -v make >/dev/null 2>&1; then
  echo "Running: make sanity"
  make sanity
else
  echo "WARNING: 'make' not found. Running generator directly..."
  $PY_CMD scripts/generate_sanity_output.py
fi

OUT="artifacts/sanity_output.json"
if [[ ! -f "$OUT" ]]; then
  echo "ERROR: Missing $OUT"
  exit 1
fi

# 3. RUN VERIFIER
$PY_CMD scripts/verify_output.py "$OUT"

echo "OK: sanity check passed"
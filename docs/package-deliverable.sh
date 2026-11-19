#!/usr/bin/env bash
# Assemble the Workada deliverable zip after recording.
# Usage:  bash docs/package-deliverable.sh ~/Downloads/shipcalc-0.3.0-py3-none-any.whl
set -euo pipefail
cd "$(dirname "$0")/.."

WHEEL="${1:-}"
OUT="shipcalc-ci-deliverable.zip"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

if [ ! -f .github/workflows/ci.yml ]; then
  echo "ERROR: .github/workflows/ci.yml not found."
  echo "Pull the workflow you committed on camera:  git pull"
  exit 1
fi
cp .github/workflows/ci.yml "$STAGE/"

if [ -n "$WHEEL" ] && [ -f "$WHEEL" ]; then
  cp "$WHEEL" "$STAGE/"
else
  echo "WARNING: no wheel given or file not found."
  echo "Download it from the Releases page, then re-run with its path."
fi

rm -f "$OUT"
( cd "$STAGE" && zip -qr "$OLDPWD/$OUT" . )
echo "Created $OUT:"
unzip -l "$OUT"

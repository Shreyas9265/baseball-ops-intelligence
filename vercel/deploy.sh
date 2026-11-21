#!/usr/bin/env bash
# Deploy the live demo to Vercel (free Hobby plan): https://baseball-ops.vercel.app
# Static UI is served by Vercel; /api/* runs the standard-library handler in a serverless function.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$(mktemp -d)"
mkdir -p "$OUT/api" "$OUT/public"
cp "$ROOT"/static/* "$OUT/public/"
cp "$ROOT/server.py" "$OUT/api/_server.py"
cp "$ROOT/vercel/index.py" "$OUT/api/index.py"
cp "$ROOT/vercel/vercel.json" "$OUT/vercel.json"
echo "3.12" > "$OUT/.python-version"
echo "# standard library only" > "$OUT/requirements.txt"
cd "$OUT" && npx vercel deploy --prod --yes --name baseball-ops

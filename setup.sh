#!/usr/bin/env bash
# The Content Forge — one-shot setup
# Installs Node deps for Remotion + Slidev, Python deps, and copies .env.example -> .env

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "[forge] Setting up the-content-forge in: $ROOT_DIR"

# 1. .env
if [ ! -f .env ]; then
  cp .env.example .env
  echo "[forge] Created .env from .env.example — fill in your credentials before running pipelines."
else
  echo "[forge] .env already exists — leaving it alone."
fi

# 2. Python deps
if command -v pip >/dev/null 2>&1; then
  echo "[forge] Installing Python deps from requirements.txt..."
  pip install -r requirements.txt
else
  echo "[forge] WARNING: pip not found — skipping Python deps. Install Python 3.10+ and re-run."
fi

# 3. Remotion deps
if [ -d tools/broll-animator ]; then
  echo "[forge] Installing Remotion deps (tools/broll-animator)..."
  (cd tools/broll-animator && npm install)
fi

# 4. Slidev deps
if [ -d harness-templates/presentations ]; then
  echo "[forge] Installing Slidev deps (harness-templates/presentations)..."
  (cd harness-templates/presentations && npm install)
fi

echo ""
echo "[forge] Done."
echo ""
echo "Next steps:"
echo "  1. Edit .env with the integrations you want to use."
echo "  2. (Optional) Customize .claude/skills/voice-standard/SKILL.md, config/theme.json, config/persona.md, config/image-style.md, .audience.txt."
echo "  3. Open Claude Code in this directory and run /create-lesson, /repurpose-social, etc."

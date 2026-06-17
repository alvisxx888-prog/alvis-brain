#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: scripts/push_vps_update.sh root@YOUR_VPS_IP"
  exit 1
fi

HOST="$1"
APP_DIR="/root/amy-vps-bot"
SERVICE_NAME="amy-vps-bot"
ARCHIVE="/tmp/amy-vps-update-$(date +%s).tgz"

if [ -z "${OPENROUTER_API_KEY:-}" ] && [ -f .env ]; then
  OPENROUTER_API_KEY="$(awk -F= '/^OPENROUTER_API_KEY=/{print $2; exit}' .env)"
fi
if [ -z "${OPENAI_API_KEY:-}" ] && [ -f .env ]; then
  OPENAI_API_KEY="$(awk -F= '/^OPENAI_API_KEY=/{print $2; exit}' .env)"
fi
if [ -z "${APIFY_API_TOKEN:-}" ] && [ -f .env ]; then
  APIFY_API_TOKEN="$(awk -F= '/^APIFY_API_TOKEN=/{print $2; exit}' .env)"
fi
if [ -z "${GAMMA_API_KEY:-}" ] && [ -f .env ]; then
  GAMMA_API_KEY="$(awk -F= '/^GAMMA_API_KEY=/{print $2; exit}' .env)"
fi

if [ -z "${OPENROUTER_API_KEY:-}" ] && [ -z "${OPENAI_API_KEY:-}" ]; then
  echo ">>> No local API keys found. Code will still be updated; existing VPS .env will be preserved."
fi

echo ">>> Packing local bot files"
tar -czf "$ARCHIVE" \
  app \
  commands \
  services \
  scripts/apply_remote_env.py \
  bot.py \
  requirements.txt \
  .env.example \
  deploy/amy-vps-bot.service

echo ">>> Uploading to $HOST"
scp "$ARCHIVE" "$HOST:/tmp/amy-vps-update.tgz"

echo ">>> Updating files and dependencies on VPS"
ssh "$HOST" "
set -euo pipefail
mkdir -p '$APP_DIR'
tar -xzf /tmp/amy-vps-update.tgz -C '$APP_DIR'
cd '$APP_DIR'
python3 -m venv venv
venv/bin/pip install -U pip
venv/bin/pip install -r requirements.txt
cp deploy/amy-vps-bot.service /etc/systemd/system/amy-vps-bot.service
if [ ! -f .env ]; then cp .env.example .env; fi
systemctl daemon-reload
"

if [ -n "${OPENROUTER_API_KEY:-}" ] && [[ "$OPENROUTER_API_KEY" == sk-or-* ]]; then
  echo ">>> Updating OpenRouter key on VPS"
  printf "%s" "$OPENROUTER_API_KEY" | ssh "$HOST" "cd '$APP_DIR' && venv/bin/python scripts/apply_remote_env.py --openrouter-key-stdin"
else
  echo ">>> OPENROUTER_API_KEY not found locally; keeping existing VPS value."
fi

if [ -n "${OPENAI_API_KEY:-}" ] && [[ "$OPENAI_API_KEY" == sk-* ]]; then
  echo ">>> Updating OpenAI key on VPS"
  printf "%s" "$OPENAI_API_KEY" | ssh "$HOST" "cd '$APP_DIR' && venv/bin/python scripts/apply_remote_env.py --openai-key-stdin"
else
  echo ">>> OPENAI_API_KEY not found locally; keeping existing VPS value."
fi

if [ -n "${APIFY_API_TOKEN:-}" ]; then
  echo ">>> Updating Apify token on VPS"
  printf "%s" "$APIFY_API_TOKEN" | ssh "$HOST" "cd '$APP_DIR' && venv/bin/python scripts/apply_remote_env.py --apify-key-stdin"
else
  echo ">>> APIFY_API_TOKEN not found locally; keeping existing VPS value."
fi

if [ -n "${GAMMA_API_KEY:-}" ]; then
  echo ">>> Updating Gamma key on VPS"
  printf "%s" "$GAMMA_API_KEY" | ssh "$HOST" "cd '$APP_DIR' && venv/bin/python scripts/apply_remote_env.py --gamma-key-stdin"
else
  echo ">>> GAMMA_API_KEY not found locally; keeping existing VPS value."
fi

echo ">>> Restarting service"
ssh "$HOST" "systemctl restart '$SERVICE_NAME' && systemctl status '$SERVICE_NAME' --no-pager -l | sed -n '1,16p'"

echo ">>> Verifying deployed build on VPS"
ssh "$HOST" "cd '$APP_DIR' && grep -n 'BOT_BUILD' bot.py && venv/bin/python -m py_compile bot.py"

rm -f "$ARCHIVE"
echo "Done. In Telegram, try /ping and /version. /ping should show the Build line."

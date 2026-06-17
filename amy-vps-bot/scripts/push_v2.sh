#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: scripts/push_v2.sh root@YOUR_VPS_IP"
  exit 1
fi

HOST="$1"
APP_DIR="/root/amy-v2"
ARCHIVE="/tmp/amy-v2-$(date +%s).tgz"

echo ">>> Packing Amy V2 files"
tar -czf "$ARCHIVE" \
  app/config_v2.py \
  app/formatting.py \
  app/__init__.py \
  services/providers_v2.py \
  bot_v2.py \
  requirements.txt \
  .env.example \
  deploy/amy-v2.service

echo ">>> Uploading to $HOST"
scp "$ARCHIVE" "$HOST:/tmp/amy-v2.tgz"

echo ">>> Installing Amy V2 on VPS"
ssh "$HOST" "
set -euo pipefail
mkdir -p '$APP_DIR'
tar -xzf /tmp/amy-v2.tgz -C '$APP_DIR'
cd '$APP_DIR'
python3 -m venv venv
venv/bin/pip install -U pip
venv/bin/pip install -r requirements.txt
cp deploy/amy-v2.service /etc/systemd/system/amy-v2.service
if [ ! -f .env ]; then cp .env.example .env; fi
systemctl daemon-reload
systemctl enable amy-v2
systemctl restart amy-v2
systemctl status amy-v2 --no-pager -l | sed -n '1,16p'
"

rm -f "$ARCHIVE"
echo "Done. Try /status_ai and /test_ai in the V2 bot."

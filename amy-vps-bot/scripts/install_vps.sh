#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/root/amy-vps-bot"
SERVICE_NAME="amy-vps-bot.service"

echo ""
echo "=================================================="
echo " Amy VPS Bot - full install"
echo "=================================================="
echo ""

echo ">>> [1/5] Installing Python runtime and media tools"
apt-get update -q
apt-get install -y python3-pip python3-venv ffmpeg pkg-config

echo ">>> [2/5] Creating app directory"
mkdir -p "$APP_DIR"
cp -r app commands services scripts bot.py requirements.txt .env.example "$APP_DIR/"
cp deploy/amy-vps-bot.service "/etc/systemd/system/$SERVICE_NAME"
chmod +x "$APP_DIR/scripts/setup_keys.sh"

echo ">>> [3/5] Installing dependencies"
cd "$APP_DIR"
python3 -m venv venv
venv/bin/pip install -U pip
venv/bin/pip install -r requirements.txt

echo ">>> [4/5] Enabling systemd service"
systemctl daemon-reload
systemctl enable amy-vps-bot

echo ">>> [5/5] Setting API keys"
bash "$APP_DIR/scripts/setup_keys.sh"

echo ""
echo "Done."
echo "Logs: journalctl -u amy-vps-bot -f"
echo "Restart: systemctl restart amy-vps-bot"
echo "Update keys: bash $APP_DIR/scripts/setup_keys.sh"

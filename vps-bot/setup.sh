#!/bin/bash
# ================================================================
# Stanley Bot — 完整安裝腳本（首次部署用）
# 用法：bash setup.sh
# ================================================================
set -e

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║      Stanley Bot v4.2 — 完整安裝                 ║"
echo "╚══════════════════════════════════════════════════╝"

# ── 系統依賴 ─────────────────────────────────────────────────
echo ""
echo ">>> [1/5] 安裝系統依賴..."
apt-get update -q
apt-get install -y python3-pip python3-venv ffmpeg

# ── 建立 bot 目錄 ──────────────────────────────────────────────
echo ">>> [2/5] 建立 bot 目錄..."
mkdir -p /root/claude-bot
cp bot.py /root/claude-bot/
cp requirements.txt /root/claude-bot/
cp claude-bot.service /etc/systemd/system/
chmod +x setup_keys.sh
cp setup_keys.sh /root/claude-bot/

# ── 安裝 Python 依賴 ──────────────────────────────────────────
echo ">>> [3/5] 安裝 Python 依賴（需要約2分鐘）..."
cd /root/claude-bot
python3 -m venv venv
venv/bin/pip install -q --upgrade pip
venv/bin/pip install -q -r requirements.txt

echo "   ✅ 已安裝：anthropic, python-telegram-bot, apscheduler"
echo "   ✅ 已安裝：openai（DALL-E 3 + Whisper）"
echo "   ✅ 已安裝：python-pptx, reportlab, pdfplumber, python-docx"
echo "   ✅ 已安裝：duckduckgo-search, apify-client"

# ── systemd service ───────────────────────────────────────────
echo ">>> [4/5] 設定 systemd service..."
systemctl daemon-reload
systemctl enable claude-bot

# ── API Keys 設定 ─────────────────────────────────────────────
echo ">>> [5/5] 設定 API Keys..."
echo ""
bash /root/claude-bot/setup_keys.sh

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  安裝完成！                                       ║"
echo "║                                                   ║"
echo "║  常用指令：                                       ║"
echo "║  查看 log：journalctl -u claude-bot -f            ║"
echo "║  重啟 bot：systemctl restart claude-bot           ║"
echo "║  更新 keys：bash /root/claude-bot/setup_keys.sh   ║"
echo "╚══════════════════════════════════════════════════╝"

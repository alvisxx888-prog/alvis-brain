#!/bin/bash
set -e

echo ">>> 安裝 Python3 + pip"
apt-get update -q && apt-get install -y python3-pip python3-venv

echo ">>> 建立 bot 目錄"
mkdir -p /root/claude-bot
cp bot.py /root/claude-bot/
cp requirements.txt /root/claude-bot/
cp claude-bot.service /etc/systemd/system/

echo ">>> 建立虛擬環境 + 安裝依賴"
cd /root/claude-bot
python3 -m venv venv
venv/bin/pip install -q -r requirements.txt

echo ""
echo "=== 完成！下一步 ==="
echo "1. 建立 .env 文件："
echo "   nano /root/claude-bot/.env"
echo ""
echo "   貼入以下內容（換成你嘅 key）："
echo "   TELEGRAM_BOT_TOKEN=你的token"
echo "   ANTHROPIC_API_KEY=你的key"
echo ""
echo "2. 啟動 service："
echo "   systemctl daemon-reload"
echo "   systemctl enable claude-bot"
echo "   systemctl start claude-bot"
echo ""
echo "3. 睇 log："
echo "   journalctl -u claude-bot -f"

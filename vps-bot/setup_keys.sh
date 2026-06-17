#!/bin/bash
# ================================================================
# Stanley Bot — 一鍵設定所有 API Keys
# 用法：bash setup_keys.sh
# ================================================================

ENV_FILE="/root/claude-bot/.env"
BASHRC="/root/.bashrc"
SERVICE="claude-bot"

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║      Stanley Bot — API Keys 設定精靈             ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ── 讀取現有 .env（如果存在）──────────────────────────────────
declare -A EXISTING
if [ -f "$ENV_FILE" ]; then
    echo "✅ 發現現有 .env，保留已有設定..."
    while IFS='=' read -r key val; do
        [[ "$key" =~ ^#.*$ ]] && continue
        [[ -z "$key" ]] && continue
        EXISTING["$key"]="$val"
    done < "$ENV_FILE"
fi

# ── 輔助函數 ──────────────────────────────────────────────────
prompt_key() {
    local KEY="$1"
    local LABEL="$2"
    local HOW_TO="$3"
    local REQUIRED="$4"

    local CURRENT="${EXISTING[$KEY]:-}"
    if [ -n "$CURRENT" ]; then
        echo "  ✅ $LABEL 已設定（${CURRENT:0:8}...）"
        echo "$KEY=$CURRENT"
        return
    fi

    echo ""
    echo "  📌 $LABEL"
    echo "     點攞：$HOW_TO"
    if [ "$REQUIRED" = "required" ]; then
        echo -n "  🔑 輸入 $KEY（必填）: "
    else
        echo -n "  🔑 輸入 $KEY（可跳過，Enter 略過）: "
    fi
    read -r VALUE
    if [ -n "$VALUE" ]; then
        echo "$KEY=$VALUE"
    elif [ "$REQUIRED" = "required" ]; then
        echo "⚠️  $KEY 未填，Bot 啟動會出錯！"
        echo "$KEY=MISSING"
    fi
}

# ── 收集所有 Keys ────────────────────────────────────────────
echo ""
echo "請逐一輸入 API Keys（已設定嘅直接跳過）："
echo "────────────────────────────────────────"

{
    echo "# Stanley Bot — API Keys"
    echo "# 生成時間：$(date '+%Y-%m-%d %H:%M')"
    echo ""

    prompt_key "TELEGRAM_BOT_TOKEN" \
        "Telegram Bot Token" \
        "Telegram 搜尋 @BotFather → /newbot → 複製 token" \
        "required"

    prompt_key "ANTHROPIC_API_KEY" \
        "Anthropic API Key（Claude AI）" \
        "console.anthropic.com → API Keys → Create Key" \
        "required"

    prompt_key "OPENAI_API_KEY" \
        "OpenAI API Key（DALL-E 3 圖片 + Whisper 語音）" \
        "platform.openai.com → API Keys → Create new secret key" \
        "optional"

    prompt_key "APIFY_API_TOKEN" \
        "Apify Token（IG/Google/小紅書 爬蟲）" \
        "apify.com 免費註冊 → Settings → Integrations → API token" \
        "optional"

    prompt_key "GAMMA_API_KEY" \
        "Gamma API Key（AI 簡報生成）" \
        "gamma.app → Settings → API → Generate API Key" \
        "optional"

} > "$ENV_FILE"

echo ""
echo "────────────────────────────────────────"
echo "✅ .env 已儲存至 $ENV_FILE"
echo ""

# ── 寫入 .bashrc 令 keys 在 systemd service 可用 ─────────────
echo "# Stanley Bot Keys — 自動加入" >> "$BASHRC"
while IFS='=' read -r key val; do
    [[ "$key" =~ ^#.*$ ]] && continue
    [[ -z "$key" || -z "$val" ]] && continue
    grep -q "export $key=" "$BASHRC" 2>/dev/null || echo "export $key=$val" >> "$BASHRC"
done < "$ENV_FILE"

# ── 更新 systemd service 令其讀取 .env ───────────────────────
SERVICE_FILE="/etc/systemd/system/${SERVICE}.service"
if [ -f "$SERVICE_FILE" ]; then
    # 加入 EnvironmentFile 行（如未有）
    if ! grep -q "EnvironmentFile" "$SERVICE_FILE"; then
        sed -i "/\[Service\]/a EnvironmentFile=$ENV_FILE" "$SERVICE_FILE"
        echo "✅ systemd service 已更新讀取 .env"
    fi
    systemctl daemon-reload
    systemctl restart "$SERVICE" && echo "✅ Bot 重啟成功" || echo "⚠️ Bot 重啟失敗，請睇 log"
else
    echo "⚠️ 找不到 service 文件，請手動重啟 bot"
fi

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  完成！查看狀態：journalctl -u claude-bot -f     ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

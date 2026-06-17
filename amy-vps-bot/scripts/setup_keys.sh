#!/usr/bin/env bash
# ================================================================
# Amy VPS Bot - one-shot API key setup
# Usage: bash scripts/setup_keys.sh
# ================================================================
set -euo pipefail

APP_DIR="${APP_DIR:-/root/amy-vps-bot}"
ENV_FILE="${ENV_FILE:-$APP_DIR/.env}"
SERVICE="${SERVICE:-amy-vps-bot}"
BASHRC="${BASHRC:-/root/.bashrc}"

mkdir -p "$APP_DIR"

echo ""
echo "=================================================="
echo " Amy VPS Bot - API Keys setup"
echo "=================================================="
echo ""

declare -A EXISTING
if [ -f "$ENV_FILE" ]; then
  echo "Found existing .env; keeping values unless you choose to replace them."
  while IFS='=' read -r key val; do
    [[ "$key" =~ ^#.*$ ]] && continue
    [[ -z "$key" ]] && continue
    EXISTING["$key"]="$val"
  done < "$ENV_FILE"
fi

prompt_key() {
  local key="$1"
  local label="$2"
  local how_to="$3"
  local required="$4"
  local current="${EXISTING[$key]:-}"

  echo ""
  echo "$label"
  echo "How to get it: $how_to"
  if [ -n "$current" ] && [[ "$current" != replace_with_* ]] && [[ "$current" != PASTE_* ]]; then
    echo "Current value exists (${current:0:8}...). Press Enter to keep it."
  fi
  if [ "$required" = "required" ]; then
    read -r -p "$key (required): " value
  else
    read -r -p "$key (optional, Enter to skip/keep): " value
  fi

  if [ -n "$value" ]; then
    echo "$key=$value"
  elif [ -n "$current" ]; then
    echo "$key=$current"
  elif [ "$required" = "required" ]; then
    echo "$key=MISSING"
    echo "Warning: $key is required before the bot can start."
  else
    echo "$key="
  fi
}

{
  echo "# Amy VPS Bot API Keys"
  echo "# Generated: $(date '+%Y-%m-%d %H:%M')"
  echo ""

  prompt_key "TELEGRAM_BOT_TOKEN" \
    "Telegram Bot Token" \
    "Telegram @BotFather -> /newbot -> copy token" \
    "required"

  prompt_key "ALLOWED_TELEGRAM_USER_IDS" \
    "Allowed Telegram User IDs" \
    "Telegram @userinfobot -> copy your numeric id; comma-separate multiple ids" \
    "required"

  prompt_key "OPENAI_API_KEY" \
    "OpenAI API Key (text, vision, image generation, Whisper)" \
    "platform.openai.com -> API keys -> create key" \
    "optional"

  prompt_key "OPENROUTER_API_KEY" \
    "OpenRouter API Key (fallback text and vision provider)" \
    "openrouter.ai -> Keys -> create key" \
    "optional"

  prompt_key "APIFY_API_TOKEN" \
    "Apify Token (IG/Threads/XHS scraping fallback)" \
    "apify.com -> Settings -> Integrations -> API token" \
    "optional"

  prompt_key "GAMMA_API_KEY" \
    "Gamma API Key (future AI deck generation hook)" \
    "gamma.app -> Settings -> API" \
    "optional"

  echo ""
  echo "# Models"
  echo "OPENAI_MODEL_FAST=${EXISTING[OPENAI_MODEL_FAST]:-gpt-4.1-mini}"
  echo "OPENAI_MODEL_HEAVY=${EXISTING[OPENAI_MODEL_HEAVY]:-gpt-4.1}"
  echo "OPENAI_IMAGE_MODEL=${EXISTING[OPENAI_IMAGE_MODEL]:-gpt-image-2}"
  echo "OPENROUTER_MODEL_FAST=${EXISTING[OPENROUTER_MODEL_FAST]:-~openai/gpt-latest}"
  echo "OPENROUTER_MODEL_HEAVY=${EXISTING[OPENROUTER_MODEL_HEAVY]:-~openai/gpt-latest}"
  echo "LOCAL_WHISPER_MODEL=${EXISTING[LOCAL_WHISPER_MODEL]:-base}"
  echo ""
  echo "# Runtime behavior"
  echo "BOT_NAME=${EXISTING[BOT_NAME]:-Amy}"
  echo "LOW_TOKEN_MODE=${EXISTING[LOW_TOKEN_MODE]:-true}"
  echo "DAILY_BRIEFING_ENABLED=${EXISTING[DAILY_BRIEFING_ENABLED]:-false}"
  echo "DAILY_BRIEFING_HOUR=${EXISTING[DAILY_BRIEFING_HOUR]:-8}"
  echo "DAILY_BRIEFING_MINUTE=${EXISTING[DAILY_BRIEFING_MINUTE]:-45}"
  echo ""
  echo "# VPS service names"
  echo "HERMES_SERVICE_NAME=${EXISTING[HERMES_SERVICE_NAME]:-hermes-agent}"
  echo "BOT_SERVICE_NAME=${EXISTING[BOT_SERVICE_NAME]:-amy-vps-bot}"
} > "$ENV_FILE"

chmod 600 "$ENV_FILE"
echo ""
echo "Saved $ENV_FILE"

if [ -f "$BASHRC" ]; then
  while IFS='=' read -r key val; do
    [[ "$key" =~ ^#.*$ ]] && continue
    [[ -z "$key" || -z "$val" || "$val" = "MISSING" ]] && continue
    if ! grep -q "export $key=" "$BASHRC" 2>/dev/null; then
      echo "export $key='$val'" >> "$BASHRC"
    fi
  done < "$ENV_FILE"
fi

service_file="/etc/systemd/system/${SERVICE}.service"
if [ -f "$service_file" ]; then
  if ! grep -q "EnvironmentFile=$ENV_FILE" "$service_file"; then
    sed -i "/\[Service\]/a EnvironmentFile=$ENV_FILE" "$service_file"
  fi
  systemctl daemon-reload
  systemctl restart "$SERVICE" && echo "Bot restarted." || echo "Bot restart failed; check journalctl -u $SERVICE -f"
else
  echo "Service file not found. Start later with: systemctl restart $SERVICE"
fi

echo ""
echo "Done. Check logs: journalctl -u $SERVICE -f"

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ENV_PATH = Path("/root/amy-vps-bot/.env")


def read_env(path: Path) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()


def upsert(lines: list[str], key: str, value: str) -> list[str]:
    updated = False
    output: list[str] = []
    for line in lines:
        if line.startswith(f"{key}="):
            output.append(f"{key}={value}")
            updated = True
        else:
            output.append(line)
    if not updated:
        output.append(f"{key}={value}")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Update Amy VPS bot env values.")
    parser.add_argument("--openrouter-key-stdin", action="store_true")
    parser.add_argument("--openai-key-stdin", action="store_true")
    parser.add_argument("--apify-key-stdin", action="store_true")
    parser.add_argument("--gamma-key-stdin", action="store_true")
    args = parser.parse_args()

    stdin_enabled = (
        args.openrouter_key_stdin
        or args.openai_key_stdin
        or args.apify_key_stdin
        or args.gamma_key_stdin
    )
    stdin_value = sys.stdin.read().strip() if stdin_enabled else ""

    lines = read_env(ENV_PATH)
    if args.openrouter_key_stdin:
        if not stdin_value.startswith("sk-or-"):
            print("OPENROUTER_API_KEY looks invalid or empty.", file=sys.stderr)
            return 1
        lines = upsert(lines, "OPENROUTER_API_KEY", stdin_value)
        lines = upsert(lines, "OPENROUTER_MODEL_FAST", "~openai/gpt-latest")
        lines = upsert(lines, "OPENROUTER_MODEL_HEAVY", "~openai/gpt-latest")
        print("Updated OPENROUTER_API_KEY and OpenRouter models.")
    if args.openai_key_stdin:
        if not stdin_value.startswith("sk-"):
            print("OPENAI_API_KEY looks invalid or empty.", file=sys.stderr)
            return 1
        lines = upsert(lines, "OPENAI_API_KEY", stdin_value)
        lines = upsert(lines, "OPENAI_MODEL_FAST", "gpt-4.1-mini")
        lines = upsert(lines, "OPENAI_MODEL_HEAVY", "gpt-4.1")
        lines = upsert(lines, "OPENAI_IMAGE_MODEL", "gpt-image-2")
        print("Updated OPENAI_API_KEY and OpenAI models.")
    if args.apify_key_stdin:
        if not stdin_value:
            print("APIFY_API_TOKEN looks empty.", file=sys.stderr)
            return 1
        lines = upsert(lines, "APIFY_API_TOKEN", stdin_value)
        print("Updated APIFY_API_TOKEN.")
    if args.gamma_key_stdin:
        if not stdin_value:
            print("GAMMA_API_KEY looks empty.", file=sys.stderr)
            return 1
        lines = upsert(lines, "GAMMA_API_KEY", stdin_value)
        print("Updated GAMMA_API_KEY.")
    if not stdin_enabled:
        print("No env update requested.", file=sys.stderr)
        return 1
    ENV_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

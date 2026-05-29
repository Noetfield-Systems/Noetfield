#!/usr/bin/env python3
"""Check Telegram bot env and webhook registration (no secrets printed)."""

from __future__ import annotations

import os
import sys


def _mask(value: str) -> str:
    value = value.strip()
    if len(value) <= 8:
        return "(set)" if value else "(missing)"
    return f"{value[:4]}…{value[-4:]}"


def main() -> int:
    enabled = os.environ.get("TELEGRAM_BOT_ENABLED", "true").lower() not in ("0", "false", "no")
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    base = os.environ.get("TELEGRAM_WEBHOOK_BASE_URL", "").strip().rstrip("/")
    secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "").strip()
    openrouter = os.environ.get("OPENROUTER_API_KEY", "").strip()
    gemini = os.environ.get("GEMINI_API_KEY", "").strip()

    print("Telegram bot diagnostics")
    print("  TELEGRAM_BOT_ENABLED:", enabled)
    print("  TELEGRAM_BOT_TOKEN:", _mask(token))
    print("  TELEGRAM_WEBHOOK_BASE_URL:", base or "(missing)")
    print("  TELEGRAM_WEBHOOK_SECRET:", _mask(secret))
    print("  LLM (openrouter):", _mask(openrouter))
    print("  LLM (gemini):", _mask(gemini))

    if not enabled:
        print("\nFAIL: TELEGRAM_BOT_ENABLED is false.")
        return 1
    if not token:
        print("\nFAIL: TELEGRAM_BOT_TOKEN is not set on this host.")
        return 1
    if not base:
        print("\nFAIL: TELEGRAM_WEBHOOK_BASE_URL is not set.")
        return 1

    expected = f"{base}/api/telegram/webhook"
    print("\nExpected webhook URL:", expected)

    try:
        from noetfield_governance.telegram_client import (
            get_me,
            get_webhook_info,
            summarize_webhook_info,
        )
    except ImportError:
        print("\nRun with PYTHONPATH including services/governance (see Makefile api-v3).", file=sys.stderr)
        return 1

    try:
        me = get_me(token=token)
        bot = me.get("result") if isinstance(me.get("result"), dict) else {}
        print("\nBot:", f"@{bot.get('username', '?')}", f"id={bot.get('id', '?')}")
        info = get_webhook_info(token=token)
        webhook = summarize_webhook_info(info)
    except Exception as exc:
        print("\nFAIL: Telegram API error:", exc)
        return 1

    registered = str(webhook.get("url") or "")
    print("Registered webhook:", registered or "(none)")
    print("Pending updates:", webhook.get("pending_update_count"))
    if webhook.get("last_error_message"):
        print("Last webhook error:", webhook.get("last_error_message"))

    ok = registered == expected and not webhook.get("last_error_message")
    if registered != expected:
        print("\nFAIL: Webhook URL mismatch. Re-register:")
        print(f"  curl -X POST '{base}/api/telegram/register-webhook' \\")
        if secret:
            print(f"    -H 'X-Admin-Secret: <your TELEGRAM_WEBHOOK_SECRET>'")
        return 1
    if webhook.get("last_error_message"):
        print("\nFAIL: Telegram cannot reach your webhook — check TLS, firewall, and API process on port 8001.")
        return 1
    if not openrouter and not gemini:
        print("\nWARN: No LLM key — /start works; free-text questions will show a configuration message.")

    print("\nOK: Webhook registered and URL matches. Send /start to your bot in Telegram.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

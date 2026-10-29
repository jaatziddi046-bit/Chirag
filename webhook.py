# api/webhook.py
# Vercel entry point — Telegram webhook receiver
# Yeh file aapke existing bot.py ko import karti hai aur webhook mode mein chalati hai

import os
import sys
from pathlib import Path

# Root directory ko sys.path mein add karo taaki bot.py import ho sake
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flask import Flask, request, jsonify
import telebot

# ── Aapka existing bot.py import karo ──────────────────────
# IMPORTANT: bot.py mein `bot.infinity_polling()` call nahi hona chahiye
# jab yeh file import ho. Isliye main() ko guard karna hoga.
import bot as bot_module

bot = bot_module.bot  # Aapka existing TeleBot instance

app = Flask(__name__)

# Webhook secret — optional but recommended
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "ok": True,
        "mode": "webhook",
        "brand": bot_module.BRAND_TAG,
        "running_bots": len(bot_module.RUNNING) if "RUNNING" in dir(bot_module) else 0,
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "alive"})


@app.route("/api/webhook", methods=["POST"])
def telegram_webhook():
    """Telegram webhook endpoint. Har update yahan aata hai."""
    # Optional: secret header check
    if WEBHOOK_SECRET:
        header_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if header_secret != WEBHOOK_SECRET:
            return jsonify({"ok": False, "error": "invalid secret"}), 403

    try:
        payload = request.get_json(force=True)
        if not payload:
            return jsonify({"ok": True})

        # TeleBot expects an Update object
        update = telebot.types.Update.de_json(payload)
        bot.process_new_updates([update])
        return jsonify({"ok": True})
    except Exception as e:
        # Log error but always return 200 so Telegram doesn't retry endlessly
        print(f"[webhook] error: {e}", flush=True)
        return jsonify({"ok": True})
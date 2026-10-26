"""Envío de mensajes a Telegram (con formato HTML). No hace nada si faltan TELEGRAM_TOKEN o TELEGRAM_CHAT_ID."""
import os

import requests


def telegram(text):
    tok, chat = os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not tok or not chat:
        print("Telegram no configurado.")
        return
    requests.post(f"https://api.telegram.org/bot{tok}/sendMessage",
                  data={"chat_id": chat, "text": text, "parse_mode": "HTML",
                        "disable_web_page_preview": "true"}, timeout=20)

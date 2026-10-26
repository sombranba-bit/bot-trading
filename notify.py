"""Envío de mensajes a Telegram. No hace nada si faltan TELEGRAM_TOKEN o TELEGRAM_CHAT_ID."""
import os

import requests


def telegram(text):
    tok, chat = os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not tok or not chat:
        print("Telegram no configurado.")
        return
    requests.post(f"https://api.telegram.org/bot{tok}/sendMessage",
                  data={"chat_id": chat, "text": text[:4000]}, timeout=20)

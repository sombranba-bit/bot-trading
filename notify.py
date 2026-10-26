"""Envío de mensajes a Telegram (con formato HTML).

Fuera de GitHub Actions, si faltan credenciales solo avisa por consola. Dentro de Actions falla,
para que un secreto mal puesto se vea en el flujo en vez de perder el mensaje en silencio.
"""
import os

import requests


def _cfg():
    tok, chat = os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not tok or not chat:
        if os.environ.get("GITHUB_ACTIONS"):
            raise RuntimeError("Faltan los secretos TELEGRAM_TOKEN o TELEGRAM_CHAT_ID")
        print("Telegram no configurado.")
        return None
    return tok, chat


def _check(r):
    if r.status_code != 200:
        raise RuntimeError(f"Telegram rechazó el mensaje ({r.status_code}): {r.text[:200]}")


def telegram(text):
    cfg = _cfg()
    if cfg:
        tok, chat = cfg
        r = requests.post(f"https://api.telegram.org/bot{tok}/sendMessage",
                          data={"chat_id": chat, "text": text, "parse_mode": "HTML",
                                "disable_web_page_preview": "true"}, timeout=20)
        _check(r)


def photo(path, caption=""):
    cfg = _cfg()
    if cfg:
        tok, chat = cfg
        with open(path, "rb") as f:
            r = requests.post(f"https://api.telegram.org/bot{tok}/sendPhoto",
                              data={"chat_id": chat, "caption": caption, "parse_mode": "HTML"},
                              files={"photo": f}, timeout=60)
        _check(r)

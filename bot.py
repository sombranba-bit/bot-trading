"""Bot en paper trading. Una ejecución = calcular votos y ajustar posiciones una vez.

Credenciales: ALPACA_API_KEY y ALPACA_API_SECRET (GitHub → Settings → Secrets).
Parar: crear un fichero KILL_SWITCH en el repo.
"""
import csv
import json
import os
from datetime import datetime, timezone

import yfinance as yf
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest

from config import CRYPTO, CRYPTO_ALPACA, MIN_VOTES, NOTIONAL, UNIVERSE
from notify import telegram
from signals import votes


def closes(ticker):
    return yf.download(ticker, period="2y", progress=False, auto_adjust=True)["Close"].squeeze()


def log_trade(symbol, action, n):
    os.makedirs("data", exist_ok=True)
    new = not os.path.exists("data/trades.csv")
    with open("data/trades.csv", "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["fecha", "simbolo", "accion", "votos"])
        w.writerow([datetime.now(timezone.utc).isoformat(timespec="minutes"), symbol, action, n])


def save_status(market_open, acciones, parado=False):
    os.makedirs("data", exist_ok=True)
    with open("data/status.json", "w") as f:
        json.dump({"ts": datetime.now(timezone.utc).isoformat(timespec="minutes"), "mercado_abierto": market_open,
                   "parado": parado, "acciones": acciones}, f)


def main() -> None:
    if os.path.exists("KILL_SWITCH"):
        print("KILL_SWITCH presente: no se opera.")
        save_status(False, [], parado=True)
        return

    screen = {}
    if os.path.exists("data/screen.json"):
        screen = json.load(open("data/screen.json"))

    trading = TradingClient(os.environ["ALPACA_API_KEY"], os.environ["ALPACA_API_SECRET"], paper=True)
    market_open = trading.get_clock().is_open
    held = {p.symbol for p in trading.get_all_positions()}
    acciones = []

    # Acciones solo con bolsa abierta; cripto siempre
    tickers = (UNIVERSE if market_open else []) + CRYPTO
    for t in tickers:
        n, _ = votes(closes(t), screen.get(t, {}).get("undervalued", False))
        want = n >= MIN_VOTES
        symbol = CRYPTO_ALPACA.get(t, t)
        key = symbol.replace("/", "")
        is_in = key in held

        if want and not is_in:
            tif = TimeInForce.GTC if t in CRYPTO else TimeInForce.DAY
            trading.submit_order(MarketOrderRequest(
                symbol=symbol, notional=NOTIONAL, side=OrderSide.BUY, time_in_force=tif))
            log_trade(symbol, "COMPRA", n)
            acciones.append(f"COMPRA {symbol}")
            telegram(f"🟢 COMPRA {symbol} · {n}/3 señales (simulación)")
            print("COMPRA", symbol, n)
        elif not want and is_in:
            trading.close_position(key)
            log_trade(symbol, "VENTA", n)
            acciones.append(f"VENTA {symbol}")
            telegram(f"🔴 VENTA {symbol} · {n}/3 señales (simulación)")
            print("VENTA", symbol, n)

    save_status(market_open, acciones)


if __name__ == "__main__":
    main()

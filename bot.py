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

from config import CRYPTO, CRYPTO_ALPACA, MAX_INVESTED, MAX_POSITIONS, MIN_VOTES, NOTIONAL, UNIVERSE
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
    positions = trading.get_all_positions()
    held = {p.symbol for p in positions}
    invested = sum(float(p.market_value) for p in positions)
    acciones = []

    # Acciones solo con bolsa abierta; cripto siempre
    tickers = (UNIVERSE if market_open else []) + CRYPTO
    decisions = []
    for t in tickers:
        n, _ = votes(closes(t), screen.get(t, {}).get("undervalued", False))
        symbol = CRYPTO_ALPACA.get(t, t)
        decisions.append((t, symbol, n, n >= MIN_VOTES, symbol.replace("/", "") in held))
    decisions.sort(key=lambda d: d[3])  # primero las ventas (False), así liberan capacidad para las compras

    for t, symbol, n, want, is_in in decisions:
        key = symbol.replace("/", "")
        if want and not is_in:
            if len(held) >= MAX_POSITIONS or invested + NOTIONAL > MAX_INVESTED:
                print("Tope alcanzado, no se compra", symbol)
                continue
            tif = TimeInForce.GTC if t in CRYPTO else TimeInForce.DAY
            trading.submit_order(MarketOrderRequest(
                symbol=symbol, notional=NOTIONAL, side=OrderSide.BUY, time_in_force=tif))
            held.add(key)
            invested += NOTIONAL
            log_trade(symbol, "COMPRA", n)
            acciones.append(f"COMPRA {symbol}")
            telegram(f"🟢 <b>COMPRA</b> {symbol}\n🎯 {n}/3 señales · <i>simulación</i>")
            print("COMPRA", symbol, n)
        elif not want and is_in:
            trading.close_position(key)
            held.discard(key)
            invested -= NOTIONAL  # aproximación: el importe real de la venta puede diferir un poco
            log_trade(symbol, "VENTA", n)
            acciones.append(f"VENTA {symbol}")
            telegram(f"🔴 <b>VENTA</b> {symbol}\n🎯 {n}/3 señales · <i>simulación</i>")
            print("VENTA", symbol, n)

    save_status(market_open, acciones)


if __name__ == "__main__":
    main()

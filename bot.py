"""Bot en paper trading. Una ejecución = ajustar las posiciones una vez.

Reglas: VT y bitcoin se compran y se mantienen. Las acciones del universo entran cuando su media de 20 días
cruza por encima de la de 100 y salen cuando cruza por debajo. Lo que haya en la cuenta fuera de eso se vende.

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

from config import ASSETS, CORE, CRYPTO, CRYPTO_ALPACA, MAX_INVESTED, MAX_POSITIONS, STOCK_BUDGET, UNIVERSE
from notify import telegram
from strategy import signal


def closes(ticker):
    return yf.download(ticker, period="2y", progress=False, auto_adjust=True)["Close"].squeeze()


def log_trade(symbol, action):
    os.makedirs("data", exist_ok=True)
    new = not os.path.exists("data/trades.csv")
    with open("data/trades.csv", "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["fecha", "simbolo", "accion", "votos"])
        w.writerow([datetime.now(timezone.utc).isoformat(timespec="minutes"), symbol, action, ""])


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

    trading = TradingClient(os.environ["ALPACA_API_KEY"], os.environ["ALPACA_API_SECRET"], paper=True)
    market_open = trading.get_clock().is_open
    positions = trading.get_all_positions()
    held = {p.symbol for p in positions}
    values = {p.symbol: float(p.market_value) for p in positions}
    invested = sum(values.values())
    acciones, avisos = [], []

    # Acciones solo con bolsa abierta; cripto siempre
    tickers = (CORE + UNIVERSE if market_open else []) + CRYPTO
    decisions = []
    for t in tickers:
        want = bool(signal(closes(t)).iloc[-1]) if t in UNIVERSE else True  # acciones: tendencia; VT y cripto: siempre
        symbol = CRYPTO_ALPACA.get(t, t)
        decisions.append((t, symbol, want, symbol.replace("/", "") in held))
    if market_open:  # posiciones que ya no forman parte de la cartera (p. ej. las acciones de la estrategia anterior)
        wanted = {d[1].replace("/", "") for d in decisions}
        decisions += [(p.symbol, p.symbol, False, True) for p in positions if p.symbol not in wanted]
    decisions.sort(key=lambda d: d[2])  # primero las ventas (False), así liberan capacidad para las compras

    for t, symbol, want, is_in in decisions:
        key = symbol.replace("/", "")
        if want and not is_in:
            amount = ASSETS.get(t, STOCK_BUDGET / len(UNIVERSE))
            if len(held) >= MAX_POSITIONS or invested + amount > MAX_INVESTED:
                print("Tope alcanzado, no se compra", symbol)
                continue
            tif = TimeInForce.GTC if t in CRYPTO else TimeInForce.DAY
            trading.submit_order(MarketOrderRequest(
                symbol=symbol, notional=amount, side=OrderSide.BUY, time_in_force=tif))
            held.add(key)
            invested += amount
            log_trade(symbol, "COMPRA")
            acciones.append(f"COMPRA {symbol}")
            avisos.append(f"🟢 <b>COMPRA</b> {symbol}")
            print("COMPRA", symbol)
        elif not want and is_in:
            trading.close_position(key)
            held.discard(key)
            invested -= values.get(key, 0)
            log_trade(symbol, "VENTA")
            acciones.append(f"VENTA {symbol}")
            avisos.append(f"🔴 <b>VENTA</b> {symbol} · sale de la estrategia")
            print("VENTA", symbol)

    if avisos:  # un solo mensaje por ejecución, para no inundar el grupo en la primera carga
        telegram("🤖 <b>Movimientos del bot</b> · <i>simulación</i>\n\n" + "\n".join(avisos))
    save_status(market_open, acciones)


if __name__ == "__main__":
    main()

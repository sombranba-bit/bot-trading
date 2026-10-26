"""Bot en paper trading (simulación). Una ejecución = revisar señales y ajustar posiciones una vez.

Credenciales: variables de entorno ALPACA_API_KEY y ALPACA_API_SECRET (en GitHub, Settings → Secrets).
Parar el bot: crear un fichero llamado KILL_SWITCH en el repo, o borrar las posiciones a mano.
"""
import os
from datetime import datetime, timedelta, timezone

from alpaca.data.enums import DataFeed
from alpaca.data.historical import CryptoHistoricalDataClient, StockHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest

from strategy import signal

STOCKS = ["SPY", "QQQ", "AAPL", "MSFT"]
CRYPTO = ["BTC/USD"]
NOTIONAL = 1000  # dólares por activo cuando la señal es comprar
LOOKBACK_DAYS = 400  # suficiente para la media de 100 días


def closes_stocks(key: str, secret: str) -> dict:
    client = StockHistoricalDataClient(key, secret)
    start = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)
    df = client.get_stock_bars(StockBarsRequest(
        symbol_or_symbols=STOCKS, timeframe=TimeFrame.Day, start=start, feed=DataFeed.IEX)).df
    return {s: df.xs(s, level="symbol")["close"] for s in STOCKS}


def closes_crypto() -> dict:
    client = CryptoHistoricalDataClient()
    start = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)
    df = client.get_crypto_bars(CryptoBarsRequest(
        symbol_or_symbols=CRYPTO, timeframe=TimeFrame.Day, start=start)).df
    return {s: df.xs(s, level="symbol")["close"] for s in CRYPTO}


def main() -> None:
    if os.path.exists("KILL_SWITCH"):
        print("KILL_SWITCH presente: no se opera.")
        return

    key, secret = os.environ["ALPACA_API_KEY"], os.environ["ALPACA_API_SECRET"]
    trading = TradingClient(key, secret, paper=True)
    market_open = trading.get_clock().is_open
    held = {p.symbol: float(p.qty) for p in trading.get_all_positions()}

    series = {**closes_crypto(), **(closes_stocks(key, secret) if market_open else {})}
    for symbol, close in series.items():
        want_in = bool(signal(close).iloc[-1])
        is_in = symbol.replace("/", "") in held
        if want_in and not is_in:
            tif = TimeInForce.GTC if "/" in symbol else TimeInForce.DAY
            trading.submit_order(MarketOrderRequest(
                symbol=symbol, notional=NOTIONAL, side=OrderSide.BUY, time_in_force=tif))
            print(f"COMPRA {symbol} por {NOTIONAL} USD")
        elif not want_in and is_in:
            trading.close_position(symbol.replace("/", ""))
            print(f"VENTA {symbol}")
        else:
            print(f"Sin cambios {symbol} (señal {'dentro' if want_in else 'fuera'})")


if __name__ == "__main__":
    main()

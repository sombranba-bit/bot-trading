"""Configuración del bot. Cambiar aquí, no en el resto del código."""

# Acciones y ETFs de EE. UU. (Alpaca solo opera aquí en paper trading)
UNIVERSE = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "JPM", "JNJ", "PG", "XOM",
    "KO", "PEP", "WMT", "HD", "V", "MA", "UNH", "PFE", "MRK", "CSCO", "INTC",
    "IBM", "ORCL", "DIS", "NKE", "MCD", "BA", "CAT", "GE", "T", "VZ", "CVX",
    "BAC", "WFC", "C", "MMM", "HON", "LLY", "ABBV", "AMGN", "SPY", "QQQ",
]

# Cripto: símbolo de Yahoo para datos y símbolo de Alpaca para órdenes
CRYPTO = ["BTC-USD"]
CRYPTO_ALPACA = {"BTC-USD": "BTC/USD"}

# Referencia: ETF global de comprar y mantener
BENCHMARK = "VWCE.DE"

NOTIONAL = 1000   # dólares simulados por activo
MIN_VOTES = 2     # comprar si al menos 2 de las 3 señales están a favor

# Criterios del screening de infravaloración
PE_MAX = 20           # P/E de beneficios máximo
UPSIDE_MIN = 0.15     # potencial mínimo según precio objetivo medio de analistas

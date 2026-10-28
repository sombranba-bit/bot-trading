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

# Cartera: importe simulado por activo que el bot compra y mantiene
CORE = ["VT"]                  # ETF del mercado mundial, equivalente más cercano a VWCE
ASSETS = {"VT": 60000, "BTC-USD": 15000}  # 60 % VT, 15 % bitcoin
STOCK_BUDGET = 25000  # 25 % en las acciones del universo, repartido a partes iguales, con tendencia 20/100
MIN_VOTES = 2     # comprar si al menos 2 de las 3 señales están a favor
DROP = 1.0              # filtro de caída desactivado (antes 0.20): se compra y se mantiene
MAX_POSITIONS = 50      # tope de posiciones abiertas a la vez (cesto de 42 más margen)
MAX_INVESTED = 110000   # tope de capital invertido (USD simulados); la cartera actual ronda los 102.000
COST = 0.002            # comisión + deslizamiento, ida y vuelta, al evaluar pronósticos
MIN_SAMPLE = 30         # pronósticos mínimos por criterio para sacar conclusiones

# Criterios del screening de infravaloración
PE_MAX = 20           # P/E de beneficios máximo
UPSIDE_MIN = 0.15     # potencial mínimo según precio objetivo medio de analistas

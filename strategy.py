"""Cruce de medias móviles: invertido cuando la media corta está por encima de la larga."""
import pandas as pd

from config import DROP

SHORT, LONG = 20, 100


def signal(close: pd.Series) -> pd.Series:
    """1 = en posición, 0 = fuera. Se usa el cierre de ayer para decidir hoy (sin mirar al futuro)."""
    fast = close.rolling(SHORT).mean()
    slow = close.rolling(LONG).mean()
    return (fast > slow).astype(int).shift(1).fillna(0)


def caida_grande(close: pd.Series) -> pd.Series:
    """True cuando el cierre está más de DROP por debajo de su máximo del último año: se sale del cesto."""
    return close < (1 - DROP) * close.rolling(252, min_periods=1).max()

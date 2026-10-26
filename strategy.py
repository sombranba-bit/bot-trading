"""Cruce de medias móviles: invertido cuando la media corta está por encima de la larga."""
import pandas as pd

SHORT, LONG = 20, 100


def signal(close: pd.Series) -> pd.Series:
    """1 = en posición, 0 = fuera. Se usa el cierre de ayer para decidir hoy (sin mirar al futuro)."""
    fast = close.rolling(SHORT).mean()
    slow = close.rolling(LONG).mean()
    return (fast > slow).astype(int).shift(1).fillna(0)

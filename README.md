# bot-trading

Bot de trading en simulación (paper trading). Todavía no opera con dinero real.

## Estado

- [x] Estrategia de cruce de medias móviles (`strategy.py`)
- [x] Backtest frente a comprar y mantener un ETF global (`backtest.py`)
- [ ] Conexión con broker en modo paper (Alpaca)
- [ ] Ejecución programada cada 30 minutos con GitHub Actions
- [ ] Informe diario

## Lanzar el backtest

En GitHub: pestaña **Actions → backtest → Run workflow**. El resultado aparece en el log del trabajo.

Hay que ejecutarlo en GitHub porque el entorno local no tiene acceso a los datos de mercado.

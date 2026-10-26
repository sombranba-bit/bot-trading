# bot-trading

Bot de trading en **simulación (paper trading)**, con informe diario y pronósticos. No opera con dinero real.

## Cómo funciona

- **Tres señales** por activo, cada una con un voto: tendencia (medias móviles), momentum (12 meses) e infravaloración (P/E bajo y precio objetivo de analistas con margen).
- Se compra si hay **al menos 2 votos** de 3. Se vende cuando baja de 2.
- **Bot** (`bot.yml`): se ejecuta cada 30 minutos y ajusta las posiciones en Alpaca paper.
- **Informe diario** (`daily.yml`): lunes a viernes, tras el cierre de EE. UU. Compara la simulación con el ETF VWCE, publica los pronósticos del día en `docs/index.md` y lo envía a Telegram si está configurado.
- Cada acción se registra la primera vez que cumple 2 y 3 votos, y se evalúa a 90 días con el exceso frente a VWCE desde su fecha.

## Ficheros

- `config.py`: universo, benchmark, criterios y tamaño de operación.
- `signals.py`: las tres señales.
- `screen.py`: screening de infravaloración (datos de Yahoo Finance, no oficiales).
- `bot.py`: órdenes en paper trading.
- `report.py`: informe y evaluación de pronósticos.
- `strategy.py`, `backtest.py`: backtest de la estrategia de medias móviles.

## Secretos necesarios (Settings → Secrets and variables → Actions)

- `ALPACA_API_KEY`, `ALPACA_API_SECRET`: claves de paper trading.
- `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`: opcionales, para recibir el informe por Telegram.

## Parar el bot

Crear un fichero llamado `KILL_SWITCH` en la raíz del repo.

## Limitaciones

- Los datos de infravaloración vienen de Yahoo Finance y pueden faltar o cambiar sin aviso.
- Los precios objetivo de analistas suelen ser optimistas.
- El backtest de 2018 a 2026 ya se ha visto, así que cualquier ajuste basado en él está contaminado. Lo que cuenta de verdad es el rendimiento en paper trading a partir de ahora.
- Esto no es asesoramiento financiero.

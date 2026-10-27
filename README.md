# bot-trading

Bot de trading en **simulación (paper trading)**, con informe diario y pronósticos. No opera con dinero real.

## Cómo funciona

- **Cesto**: el bot mantiene todas las acciones del universo (42) y cripto, con el mismo importe cada una.
- **Filtro de caída**: si una acción cae más de un 20 % desde su máximo del último año, se vende. Vuelve a entrar al recuperarse.
- **Pronósticos** (informativos, no operan): tres señales por activo (tendencia, momentum e infravaloración). Se publican en el panel y se evalúan a 90 días.
- **Bot** (`bot.yml`): se ejecuta cada 30 minutos y ajusta las posiciones en Alpaca paper. Un solo aviso de Telegram por ejecución con los movimientos.
- **Informe diario** (`daily.yml`): lunes a viernes, tras el cierre de EE. UU. Compara la simulación con el ETF VWCE, publica los pronósticos del día en `docs/index.html` y lo envía a Telegram si está configurado.
- Cada acción se registra la primera vez que cumple 2 y 3 votos, y se evalúa a 90 días con el exceso frente a VWCE desde su fecha.

## Ficheros

- `config.py`: universo, benchmark, criterios y tamaño de operación.
- `signals.py`: las tres señales.
- `screen.py`: screening de infravaloración (datos de Yahoo Finance, no oficiales).
- `bot.py`: órdenes en paper trading.
- `report.py`: datos del informe y evaluación de pronósticos.
- `page.py`: diseño de la página del informe.
- `strategy.py`: filtro de caída y medias móviles (esta última solo para el backtest).
- `backtest.py`: compara el cesto con filtro, el cesto sin filtro, la tendencia por activo y VWCE (`data/backtest.csv`).

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

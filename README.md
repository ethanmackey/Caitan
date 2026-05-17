# Catan Simulation Analytics Pipeline

This project simulates traditional 4-player base Catan with completely random AI agents and turns the results into structured analytical datasets. It is positioned as a junior data-engineering portfolio project: a Python batch pipeline generates event data, validates outputs, writes raw and mart CSVs, loads a typed SQLite database, and powers a Streamlit dashboard.

## Why this is useful for data engineering

- **Python batch pipeline:** runs repeatable simulations and captures game, player, turn, action, and resource-event records.
- **Faithful rules engine:** models 4-player setup order, robber behavior, ports, bank trades, development cards, piece limits, Longest Road, and Largest Army.
- **Data modeling:** separates raw game outcomes from analytical marts such as win rates, resource values, and development-card values.
- **Data quality:** validates completed game states for missing winners, invalid winner IDs, negative resources, and negative victory points.
- **SQL analytics:** loads results into typed SQLite tables and includes example analytical queries.
- **Visualization:** includes a Streamlit dashboard for win-rate, game-length, resource, and action analysis.

## Pipeline architecture

```text
Catan game engine
      |
      v
Python simulation batch job
      |
      +--> data/output/raw/games.csv
      +--> data/output/raw/player_games.csv
      +--> data/output/raw/turns.csv
      +--> data/output/raw/actions.csv
      +--> data/output/raw/resource_events.csv
      +--> data/output/raw/validation_errors.csv
      |
      +--> data/output/marts/player_win_rates.csv
      +--> data/output/marts/resource_values.csv
      +--> data/output/marts/dev_card_values.csv
      |
      v
SQLite analytical database
      |
      +--> reusable SQL queries in sql/
      +--> scripts/validate_data.py
      +--> dashboard/app.py
```

## Quick start

Run a small pipeline locally:

```powershell
python main.py --players 4 --games 100 --output-dir data/output --sqlite-path data/catan_analytics.db
```

Run without writing files:

```powershell
python main.py --players 4 --games 10 --no-write
```

Run tests:

```powershell
python -m unittest discover -s tests
```

Validate generated data and write a report:

```powershell
python scripts/validate_data.py --db-path data/catan_analytics.db --report-path reports/data_quality_report.md
```

Launch the dashboard after generating the database:

```powershell
streamlit run dashboard/app.py
```

## Main outputs

### Raw tables

| Dataset | Description |
| --- | --- |
| `games` | One row per completed game with turn count, player count, winner ID, and winner score. |
| `player_games` | One row per player per game with victory points, resource totals, dev-card counts, largest army, and longest road flags. |
| `turns` | One row per player turn with dice roll, action count, VP start/end, and robber movement. |
| `actions` | One row per action selected by the random agent during a turn. |
| `resource_events` | One row per net per-turn resource movement by player and resource. |
| `validation_errors` | Data-quality issues found after completed games. Empty means no validation errors were found. |

### Mart tables

| Dataset | Description |
| --- | --- |
| `player_win_rates` | Win count and win rate by player ID. |
| `resource_values` | Normalized resource values adjusted by tile availability. |
| `dev_card_values` | Normalized development-card values adjusted by deck frequency. |

## Example SQL analysis

After generating `data/catan_analytics.db`, run the queries in [`sql/`](sql/):

- [`average_game_length.sql`](sql/average_game_length.sql)
- [`dev_card_effectiveness.sql`](sql/dev_card_effectiveness.sql)
- [`player_win_rates.sql`](sql/player_win_rates.sql)
- [`resource_win_correlation.sql`](sql/resource_win_correlation.sql)

Example with SQLite:

```powershell
sqlite3 data/catan_analytics.db ".read sql/player_win_rates.sql"
```

## Resume framing

**Catan Analytics Pipeline** — Python, SQL, SQLite, Streamlit, Plotly, CSV, unittest

- Built a Python batch pipeline that simulates Catan games and generates structured game, player, turn, action, and resource-event datasets for downstream analysis.
- Designed a typed SQLite schema and SQL queries to analyze win rates, game length, resource production, development-card effectiveness, and player action trends.
- Added data-quality checks, automated tests, and a Streamlit dashboard to validate pipeline outputs and visualize game trends for non-technical users.

## Future upgrades

- Add dashboard screenshots to `assets/`.
- Add a small run-summary report with row counts and headline insights.
- Export Parquet files as an optional next step.
- Store run metadata such as random seed, pipeline timestamp, and code version.

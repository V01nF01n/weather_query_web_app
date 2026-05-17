# Weather Query App

Async web application on FastAPI that allows users to enter a city name, fetch current weather data from OpenWeatherMap, and store/display the full query history with filtering, caching, rate limiting, and CSV export.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | FastAPI (async) |
| Database | PostgreSQL 16 |
| ORM / Migrations | SQLAlchemy 2.0 (async) + Alembic |
| Cache / Rate limit | Redis 7 |
| Templates | Jinja2 |
| Settings | pydantic-settings + `.env` |
| Tests | pytest + pytest-asyncio |
| Containerisation | Docker + Docker Compose |

---

## Features

- **Weather fetching** — OpenWeatherMap API, Celsius / Fahrenheit toggle, unit stored per query
- **Query history** — full PostgreSQL persistence, every request saved (including cache hits)
- **Pagination** — configurable page size (default 10)
- **Filtering** — by city (case-insensitive substring) and date range (`from` / `to`)
- **5-minute cache** — same city within 5 minutes skips external API call; query row is still written with `served_from_cache = true`; UI shows a "Served from cache" badge
- **Per-IP rate limiting** — 30 requests / minute via Redis; returns HTTP 429 with a friendly message
- **CSV export** — filtered history exported as `.csv`
- **Structured JSON logging** — request start/end, errors, external API latency

---

## Project Structure

```
weather_query_app/
├── app/
│   ├── api/v1/endpoints/  
│   ├── core/              
│   ├── db/                
│   ├── models/             
│   ├── repositories/       
│   ├── schemas/            
│   ├── services/           
│   ├── templates/          
│   └── main.py
├── migrations/            
├── tests/
│   ├── conftest.py         
│   ├── test_query_service.py  
│   ├── test_rate_limit.py      
│   └── test_history_logic.py  
├── .env.sample
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml
```

---

## Quickstart with Docker Compose

```bash
# 1. Clone the repository
git clone https://github.com/V01nF01n/weather_query_web_app.git
cd weather_query_web_app

# 2. Create environment file
cp .env.sample .env

# 3. Add your OpenWeatherMap API key to .env
#    OPENWEATHER_API_KEY=your_key_here
#    Get a free key at https://openweathermap.org/api

# 4. Start all services (app + postgres + redis)
docker compose up --build

# 5. Open the app
# http://localhost:8000
```

Migrations run automatically on container start (`alembic upgrade head`).

---

## Local Development

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -e ".[dev]"

# 3. Set up environment variables
cp .env.sample .env
# Edit .env: set DATABASE_URL, REDIS_URL, OPENWEATHER_API_KEY

# 4. Run DB migrations
alembic upgrade head

# 5. Start the dev server
uvicorn app.main:app --reload
```

---

## Environment Variables

Copy `.env.sample` and fill in the values:

```env
APP_NAME=Weather Query App
DEBUG=false

# PostgreSQL
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/weather

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenWeatherMap
OPENWEATHER_API_KEY=your_openweather_api_key
OPENWEATHER_BASE_URL=https://api.openweathermap.org/data/2.5

# Rate limiting
RATE_LIMIT_PER_MINUTE=30

# Cache
CACHE_TTL_SECONDS=300

# Pagination
PAGE_SIZE_DEFAULT=10

# Health check
EXTERNAL_API_TIMEOUT_SECONDS=10
```

---

## API Endpoints

### Web UI

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Main page — city form + link to history |
| `POST` | `/api/weather` | Submit city form, returns result page (HTML) |
| `GET` | `/history` | History page with filters and pagination |

### JSON API

| Method | Path | Query params | Description |
|---|---|---|---|
| `GET` | `/api/weather` | `city`, `unit` | Fetch weather, returns JSON |
| `GET` | `/api/history` | `page`, `page_size`, `city`, `date_from`, `date_to` | Paginated history, returns JSON |
| `GET` | `/export.csv` | `city`, `date_from`, `date_to` | CSV export (same filters as history) |
| `GET` | `/health` | — | DB + external API health check |

### Example requests

```bash
# Fetch weather in JSON
curl "http://localhost:8000/api/weather?city=Berlin&unit=fahrenheit"

# Paginated history filtered by city and date range
curl "http://localhost:8000/api/history?city=lon&date_from=2026-01-01&date_to=2026-01-31&page=1"

# Export filtered history as CSV
curl "http://localhost:8000/export.csv?city=Berlin" -o history.csv

# Health check
curl "http://localhost:8000/health"
```

---

## Caching Behaviour

If the same city is queried within **5 minutes**, the app returns the previously fetched weather without calling OpenWeatherMap. A new row is still written to the database with `served_from_cache = true`. The history page and API response show a **"Served from cache"** badge for these entries.

Cache TTL is configurable via `CACHE_TTL_SECONDS` (default: 300 seconds).

---

## Rate Limiting

Requests to the weather fetch endpoint are limited to **30 per minute per IP address** (configurable via `RATE_LIMIT_PER_MINUTE`). When the limit is exceeded, the API returns:

```json
HTTP 429 Too Many Requests
{"detail": "Rate limit exceeded. Please wait before making another request."}
```

Rate-limited requests do not write to the database and do not call the external API.

---

## Running Tests

```bash
pytest
```

Test coverage includes:

- **`test_query_service.py`** — cache hit skips external API call; fresh fetch writes to cache and DB
- **`test_rate_limit.py`** — rate-limited request returns 429 and makes no DB write
- **`test_history_logic.py`** — filters and pagination parameters are correctly passed to the repository

All tests use fake in-memory implementations (no real DB or Redis needed).

---

## Logging

All events are logged as structured JSON (or `key=value`) to stdout:

```json
{"event": "request_start", "method": "GET", "path": "/api/weather", "request_id": "abc123"}
{"event": "external_api_call", "city": "London", "latency_ms": 241, "status": 200}
{"event": "request_end", "status_code": 200, "duration_ms": 245, "request_id": "abc123"}
```

Set `DEBUG=true` in `.env` to enable verbose logging.

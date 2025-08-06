# Copilot Instructions for Wealth App

## Project Overview
- Wealth App is a full-stack personal finance and mood tracking application.
- **Backend:** Python FastAPI (async), PostgreSQL (async SQLAlchemy), Redis (caching, rate limiting), JWT auth, advanced patterns (rate limiting, retries, circuit breaker, queueing).
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS.

## Key Backend Structure
- `app/main.py`: FastAPI app entrypoint. Routers are registered here.
- `app/api/`: API route modules, organized by version and feature (e.g., `api_v1/endpoints/`).
- `app/core/`: Core utilities (config, security, Redis, rate limiter, etc.).
- `app/db/`: Async SQLAlchemy models (`models/`), session, and base.
- `app/schemas/`: Pydantic schemas for request/response validation.
- `app/tests/`: Pytest-based backend tests.

## Essential Patterns & Conventions
- **Async everywhere:** All DB and API operations are async.
- **Pydantic for validation:** All request/response models use Pydantic schemas, never SQLAlchemy models directly in FastAPI responses.
- **JWT Auth:** All protected endpoints require JWT; see `app/core/security.py`.
- **Redis:** Used for caching, rate limiting, and background tasks. See `app/core/redis.py` and `app/core/rate_limiter.py`.
- **Error handling:** Use FastAPI's HTTPException for API errors.
- **API versioning:** All endpoints are under `/api/v1/`.
- **Testing:** Use pytest; fixtures in `tests/conftest.py`.

## Developer Workflows
- **Backend dev:**
  - Create venv, install with `pip install -r requirements.txt`.
  - Run: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
  - Test: `pytest`
- **Frontend dev:**
  - `npm install && npm run dev` in `frontend/`.
- **API docs:** Swagger at `/docs`, ReDoc at `/redoc`.

## Integration Points
- **Frontend-backend:** REST API, see `frontend/src/api/client.ts`.
- **External services:** PostgreSQL, Redis (URLs in `.env`).
- **Background jobs:** Use Redis queue (see `app/core/queue.py`).

## Project-Specific Notes
- **Never use SQLAlchemy models as FastAPI response models.** Always use Pydantic schemas.
- **All new endpoints must be async and use dependency injection for DB/session/auth.**
- **Rate limiting and retries:** Use decorators/utilities from `core/` as needed.
- **Sensitive config:** Use `.env` and `pydantic-settings` for all secrets/URLs.



## GPT OSS Agent Integration
**Agent service:**
The GPT OSS agent lives in `gpt_oss_agent.py` as a standalone FastAPI app, usually in its own directory or container.
It exposes a POST `/generate` endpoint that accepts JSON `{ "prompt": string }` and returns `{ "text": string }`.

**Async client:**
The backend asynchronously calls the GPT OSS agent using `app/ai_client.py`.
This module defines an async function `generate_text(prompt: str) -> str` that uses `httpx.AsyncClient` to call the agent's `/generate` endpoint.
The agent URL is configurable via the environment variable `GPT_AGENT_URL` (e.g., `http://gpt-oss-agent:5000/generate`).

**API route:**
A new FastAPI router is defined in `app/api/api_v1/endpoints/agent.py` under the path `/agent/gpt-oss`.
This POST endpoint accepts a JSON prompt, calls the async client, and returns the generated text. Errors are handled with HTTPException for proper HTTP responses.

**Environment variables:**
Use `.env` files or Docker Compose environment settings to configure `GPT_AGENT_URL` for flexibility in different deployment scenarios.

**Docker orchestration:**
The project supports a dual-container architecture with separate containers for the GPT OSS agent and the backend.

`gpt_oss_agent/Dockerfile` builds the agent container exposing port 5000.

`backend/Dockerfile` builds the backend exposing port 8000.

`docker-compose.yml` orchestrates both containers, with the backend depending on the agent service and connecting via Docker's internal network.
Ports 5000 (agent) and 8000 (backend) are mapped to the host.

## Troubleshooting & Common Fixes for GPT OSS Integration and Backend
**Dependency versions:**
Make sure `requirements.txt` uses available package versions, for example:

Use `aiobreaker==1.2.0` instead of non-existent 1.4.0.

Replace deprecated `aioredis` with `redis` package for compatibility with Python 3.11+.

**SQLAlchemy vs. Pydantic models:**
FastAPI response models must use Pydantic schemas (`app/schemas/`) and never SQLAlchemy models (`app/db/models/`) directly.
Errors like `Optional[app.db.models.user.User] is not a valid Pydantic field type` indicate incorrect type annotations.
Update all endpoint and dependency type hints to use Pydantic schema classes.

**Clear Python caches:**
Stale `.pyc` files or `__pycache__` folders can cause mysterious errors. Clear them with:

```bash
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

**Docker networking:**
Confirm service names and ports in `docker-compose.yml` align with environment variables.
For example, ensure `GPT_AGENT_URL=http://gpt-oss-agent:5000/generate` matches the service name `gpt-oss-agent` in the compose network.

**Server startup:**
Use `uvicorn` to start FastAPI services, not `flask run`.
Example for agent:

```bash
uvicorn gpt_oss_agent:app --host 0.0.0.0 --port 5000
```
Example for backend:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Key Examples to Reference
- Endpoint structure and async patterns: `app/api/api_v1/endpoints/`
- Pydantic schema usage and conventions: `app/schemas/`
- Async Redis client usage: `app/core/redis.py`
- GPT OSS agent and async client integration:
  - `gpt_oss_agent.py`
  - `app/ai_client.py`

---

For more, see the project [README.md](../README.md).

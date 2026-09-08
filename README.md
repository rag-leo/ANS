# ANS — Agri-News Intelligence System

Multi-source agri-news ingestion (Agrowon, ET Agriculture, Krishi Jagran) with
RAG-based search and generation (WhatsApp/push/newsletter), served by a
FastAPI backend and a Streamlit frontend.

## Architecture

- `backend/api/` — FastAPI app (search, generation, publish, analytics,
  evaluation). Deploys as an **Azure Container App**.
- `backend/data/pipeline.py` — the ingestion orchestrator
  (`run_pipeline()` / `--dry-run`), registry-driven across all three
  sources (`backend/ingestion/adapters/registry.py`). Deploys as an
  **Azure Container App Job** (run-to-completion, scheduled), using the
  *same image* as the backend API with the command overridden.
- `frontend/` — Streamlit app, a pure HTTP client of the backend API (see
  `frontend/api_client.py` — no direct imports of `backend.*`). Deploys
  separately to **Azure App Service** as native Python (no container,
  no Selenium/pgvector dependency there).
- Postgres + pgvector, and Azure OpenAI (embedding + chat + a separate
  classification deployment — see below) are external dependencies, not
  provisioned by anything in this repo.

Deployment is triggered from **Azure Repos** (`azure-pipelines.yml`), per
company policy — not from GitHub directly.

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # fill in real values, see below

alembic upgrade head   # needs a reachable Postgres with pgvector enabled

python -m backend.data.pipeline --dry-run   # sanity-check ingestion
uvicorn backend.api.main:app --reload       # backend, separate terminal

cd frontend
pip install -r requirements.txt
streamlit run app.py                        # frontend, separate terminal
```

Agrowon's adapter is Selenium-based and needs a real Chrome/Chromium on
`PATH` for local runs — ET Agriculture and Krishi Jagran are plain HTTP and
don't.

## Required configuration

Backend (`.env` locally; Application Settings / secrets in Azure) — see
`.env.example` for the full list:

- `PROJECT_NAME`, `PROJECT_VERSION`, `ENVIRONMENT`
- `API_HOST`, `API_PORT`, `API_PREFIX`
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`,
  `POSTGRES_DB`, `POSTGRES_SSLMODE` (`require` for Azure Database for
  PostgreSQL)
- `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_VERSION`
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` — the text-embedding model
- `AZURE_OPENAI_CHAT_DEPLOYMENT` — used for WhatsApp/push/newsletter
  generation
- `AZURE_OPENAI_CLASSIFICATION_DEPLOYMENT` — **deliberately separate** from
  the deployment above; used only for ingestion-time crop/category
  classification (Stage 9). Point this at a cheap deployment (e.g.
  gpt-4o-mini) — using the same deployment as generation works but defeats
  the point of having a cheaper one.
- `ALLOWED_ORIGINS` — must include the deployed frontend's URL in production
- `LOG_LEVEL`

Ingestion container only (already defaulted in the Dockerfile, override only
if your Chromium install differs):
- `CHROME_BINARY_PATH` (default `/usr/bin/chromium`)
- `CHROMEDRIVER_PATH` (default `/usr/bin/chromedriver`)

Frontend (App Service Application Settings):
- `BACKEND_API_URL` — the backend Container App's URL. Read directly as an
  environment variable by `api_client.py` (not via `st.secrets`, which
  App Service doesn't populate).

## Docker

One image serves both the backend API and the ingestion job:

```bash
docker build -t ans-backend .

# API
docker run -p 8000:8000 --env-file .env ans-backend

# Ingestion (dry run)
docker run --env-file .env ans-backend python -m backend.data.pipeline --dry-run

# Ingestion (real run)
docker run --env-file .env ans-backend python -m backend.data.pipeline
```

## Running migrations

`alembic upgrade head` is **not** run automatically on deploy (see
`azure-pipelines.yml`) — deliberately, to avoid concurrent-migration races
and keep schema changes an explicit, reviewable action. Run it manually
against the target Postgres whenever a new migration lands:

```bash
docker run --env-file .env ans-backend alembic upgrade head
```

In Azure, the equivalent is a manually-triggered Container App Job (using
the same image, command `alembic upgrade head`) run once via
`az containerapp job start` — set this up as a separate Job resource from
the scheduled ingestion Job, since one runs on a cron and the other should
only run when you say so.

## Deploying (Azure Repos → Azure)

`azure-pipelines.yml` builds the backend image, pushes it to your Azure
Container Registry, and deploys:
1. the backend Container App (new image),
2. the ingestion Container App Job (new image — its command and cron
   schedule are configured once on the Job resource itself, not by the
   pipeline),
3. the frontend to App Service (zip deploy of `frontend/`, native Python,
   `frontend/startup.sh` as the startup command).

Before the first run, fill in the placeholders at the top of
`azure-pipelines.yml` (ACR name, resource group, Container App / Job / App
Service names, and your Azure DevOps service connection names) and wire up
the actual Azure Pipeline resource in Azure DevOps — none of that can be
done from a repo file alone.

The ingestion Container App Job should be configured with a **Scheduled**
trigger (cron, UTC) for the daily run — convert your target local time to
UTC when setting the schedule.

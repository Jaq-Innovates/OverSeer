# OverSeer Backend (rough draft)

FastAPI + SQLAlchemy. Pulls real-world events from GDELT and ACLED into one normalized `events` table, and serves events, posts and personas to the frontend.

## Run
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload     # http://localhost:8000/docs
python test_api.py                # offline smoke test
```

## Database
- No `DATABASE_URL` set: local SQLite file `overseer.db` (fallback).
- PostgreSQL (primary): `DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/overseer`

| Table | Holds |
|---|---|
| `events` | GDELT/ACLED events, normalized; `raw` keeps the original record for lineage |
| `personas` | Persona profiles (traits come from the sponsor's agents) |
| `runs` | One simulation run: `seed` + `params` for reproducibility |
| `posts` | Synthetic posts, each linked to `event_id` or `injection_id`; `parent_id` for replies |
| `actions` | Likes, reposts, follows, unfollows |
| `injections` | Trainer-injected narratives |

## Endpoints
| Method | Path | Notes |
|---|---|---|
| GET | `/events` | filters: `source`, `country`, `event_type`, `start`, `end`, `limit`, `offset` |
| GET | `/events/{id}` | includes `linked_posts` count and raw record |
| POST | `/ingest/gdelt` | `{timestamp?, country?, root_codes?}`: one 15-min GDELT file, latest if no timestamp |
| POST | `/ingest/acled` | `{country, start, end, limit?}`: needs `ACLED_USERNAME` / `ACLED_PASSWORD` env vars |
| GET | `/posts` | filters: `run_id`, `narrative`, `persona_type`, `event_id` |
| GET | `/personas` | filter: `persona_type` |

## Known gaps
- GDELT pulls one 15-minute file per call; a 30-day backfill needs a loop or BigQuery.
- ACLED uses its OAuth API: each person needs their own acleddata.com account. Never commit credentials.
- Tables are created on startup; move to Alembic migrations once the schema settles.

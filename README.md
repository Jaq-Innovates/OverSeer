# OverSeer

Team A18 Senior Design Project, sponsored by ARCONTRA.

A sandbox that replays real-world events (GDELT / ACLED) into a simulated social network (OASIS) so analysts can inject narratives and measure their spread.

## Stack
- **Data/Sim:** Python ETL (GDELT, ACLED), OASIS simulation
- **Backend:** FastAPI, PostgreSQL (primary), SQLite (fallback / OASIS native log)
- **Frontend:** React / Next.js, Tailwind (SynthFeed UI)

## Layout
```
data/      ingestion + normalization
sim/       OASIS config and persona plug-in
backend/   FastAPI service
frontend/  SynthFeed UI
docs/      design docs, diagrams
```

## Team
| Area | Members |
|---|---|
| Data / Simulation | Joseph, Sami |
| API / Backend / Database | Manny, Michael |
| Front End | Rowan |
| QA / Analytics | Andres |

## Contributing
Branch off `main`, keep commits small and descriptive, open a PR for review. Never commit `.env`, API keys, or sponsor data.

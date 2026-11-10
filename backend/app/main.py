from datetime import date

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import ingest
from .db import Base, engine, get_session
from .models import Event, Persona, Post

# ponytail: create_all on startup; switch to Alembic migrations once the schema settles
Base.metadata.create_all(engine)

app = FastAPI(title="OverSeer API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------- Events ----------

@app.get("/events")
def list_events(source: str | None = None, country: str | None = None, event_type: str | None = None,
                start: date | None = None, end: date | None = None,
                limit: int = 50, offset: int = 0, s: Session = Depends(get_session)):
    q = select(Event)
    if source:
        q = q.where(Event.source == source)
    if country:
        q = q.where(Event.country == country)
    if event_type:
        q = q.where(Event.event_type == event_type)
    if start:
        q = q.where(Event.event_date >= start)
    if end:
        q = q.where(Event.event_date <= end)
    total = s.scalar(select(func.count()).select_from(q.subquery()))
    rows = s.scalars(q.order_by(Event.event_date.desc()).limit(min(limit, 500)).offset(offset)).all()
    return {"total": total, "items": [_event(e) for e in rows]}


@app.get("/events/{event_id}")
def get_event(event_id: str, s: Session = Depends(get_session)):
    e = s.get(Event, event_id)
    if not e:
        raise HTTPException(404, "Event not found")
    posts = s.scalar(select(func.count()).where(Post.event_id == event_id))
    return {**_event(e), "linked_posts": posts, "raw": e.raw}


def _event(e: Event):
    return {k: getattr(e, k) for k in ("id", "source", "event_date", "event_type", "sub_event_type", "actor1",
                                       "actor2", "country", "location", "lat", "lon", "fatalities", "tone",
                                       "source_url", "notes")}


# ---------- Ingestion ----------

class GdeltIngest(BaseModel):
    timestamp: str | None = None  # YYYYMMDDHHMMSS, latest if omitted
    country: str | None = None    # FIPS code
    root_codes: list[str] | None = None


class AcledIngest(BaseModel):
    country: str
    start: date
    end: date
    limit: int = 5000


@app.post("/ingest/gdelt")
def ingest_gdelt(body: GdeltIngest, s: Session = Depends(get_session)):
    return {"ingested": ingest.ingest_gdelt(s, body.timestamp, body.country, body.root_codes)}


@app.post("/ingest/acled")
def ingest_acled(body: AcledIngest, s: Session = Depends(get_session)):
    try:
        n = ingest.ingest_acled(s, body.country, body.start.isoformat(), body.end.isoformat(), body.limit)
    except RuntimeError as err:
        raise HTTPException(400, str(err))
    return {"ingested": n}


# ---------- Feed (read side for the frontend) ----------

@app.get("/posts")
def list_posts(run_id: int | None = None, narrative: str | None = None, persona_type: str | None = None,
               event_id: str | None = None, limit: int = 50, offset: int = 0, s: Session = Depends(get_session)):
    q = select(Post, Persona).join(Persona, Post.persona_id == Persona.id)
    if run_id:
        q = q.where(Post.run_id == run_id)
    if narrative:
        q = q.where(Post.narrative == narrative)
    if persona_type:
        q = q.where(Persona.persona_type == persona_type)
    if event_id:
        q = q.where(Post.event_id == event_id)
    rows = s.execute(q.order_by(Post.sim_time.desc()).limit(min(limit, 500)).offset(offset)).all()
    return [{"id": p.id, "text": p.text, "sim_time": p.sim_time, "narrative": p.narrative, "event_id": p.event_id,
             "parent_id": p.parent_id, "is_synthetic": p.is_synthetic,
             "persona": {"id": u.id, "name": u.name, "handle": u.handle, "type": u.persona_type}} for p, u in rows]


@app.get("/personas")
def list_personas(persona_type: str | None = None, limit: int = 50, offset: int = 0, s: Session = Depends(get_session)):
    q = select(Persona)
    if persona_type:
        q = q.where(Persona.persona_type == persona_type)
    return s.scalars(q.limit(min(limit, 500)).offset(offset)).all()

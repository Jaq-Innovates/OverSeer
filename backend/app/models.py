from datetime import date, datetime, timezone

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def now():
    return datetime.now(timezone.utc)


class Event(Base):
    """A real-world event from GDELT or ACLED, normalized to one shape."""
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # "GDELT-<id>" / "ACLED-<id>"
    source: Mapped[str] = mapped_column(String(10), index=True)     # gdelt | acled
    source_id: Mapped[str] = mapped_column(String(64))
    event_date: Mapped[date] = mapped_column(Date, index=True)
    event_type: Mapped[str | None] = mapped_column(String(80), index=True)
    sub_event_type: Mapped[str | None] = mapped_column(String(80))
    actor1: Mapped[str | None] = mapped_column(String(200))
    actor2: Mapped[str | None] = mapped_column(String(200))
    country: Mapped[str | None] = mapped_column(String(80), index=True)
    location: Mapped[str | None] = mapped_column(String(200))
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)
    fatalities: Mapped[int | None] = mapped_column(Integer)  # ACLED only
    tone: Mapped[float | None] = mapped_column(Float)        # GDELT only
    source_url: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    raw: Mapped[dict] = mapped_column(JSON)  # original record, kept for lineage
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Persona(Base):
    __tablename__ = "personas"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    handle: Mapped[str] = mapped_column(String(60), unique=True)
    persona_type: Mapped[str] = mapped_column(String(40), index=True)  # Local resident, Journalist, ...
    traits: Mapped[dict] = mapped_column(JSON, default=dict)          # filled from sponsor's agent profiles


class Run(Base):
    """One simulation run. Seed + params make it reproducible."""
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    seed: Mapped[int] = mapped_column(Integer)
    params: Mapped[dict] = mapped_column(JSON, default=dict)  # geography, period, persona mix, volume, speed
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Injection(Base):
    __tablename__ = "injections"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"), index=True)
    narrative: Mapped[str] = mapped_column(String(80))
    text: Mapped[str] = mapped_column(Text)
    sim_time: Mapped[datetime] = mapped_column(DateTime)


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)  # PST-000001
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"), index=True)
    persona_id: Mapped[str] = mapped_column(ForeignKey("personas.id"), index=True)
    event_id: Mapped[str | None] = mapped_column(ForeignKey("events.id"), index=True)
    injection_id: Mapped[int | None] = mapped_column(ForeignKey("injections.id"))
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("posts.id"))  # set for replies/quotes
    narrative: Mapped[str | None] = mapped_column(String(80), index=True)
    text: Mapped[str] = mapped_column(Text)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True)
    sim_time: Mapped[datetime] = mapped_column(DateTime, index=True)


class Action(Base):
    """Non-post interactions: like, repost, follow, unfollow, ..."""
    __tablename__ = "actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"), index=True)
    persona_id: Mapped[str] = mapped_column(ForeignKey("personas.id"), index=True)
    action_type: Mapped[str] = mapped_column(String(20), index=True)
    target_post_id: Mapped[str | None] = mapped_column(ForeignKey("posts.id"))
    target_persona_id: Mapped[str | None] = mapped_column(ForeignKey("personas.id"))
    sim_time: Mapped[datetime] = mapped_column(DateTime)

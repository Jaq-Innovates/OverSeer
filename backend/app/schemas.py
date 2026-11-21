from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Generic, TypeVar

T = TypeVar("T")


class EventSummary(BaseModel):
    id: str
    label: str


class EventOut(BaseModel):
    id: str
    source: str
    event_date: date
    event_type: str | None = None
    sub_event_type: str | None = None
    actor1: str | None = None
    actor2: str | None = None
    country: str | None = None
    location: str | None = None
    lat: float | None = None
    lon: float | None = None
    fatalities: int | None = None
    tone: float | None = None
    source_url: str | None = None
    notes: str | None = None


class PersonaSummary(BaseModel):
    id: str
    name: str
    handle: str
    persona_type: str
    model_config = ConfigDict(from_attributes=True)


class PostOut(BaseModel):
    id: str
    run_id: int
    text: str
    timestamp: datetime
    persona: PersonaSummary
    source_event: EventSummary | None = None   # None for injected posts
    parent_id: str | None = None
    narrative: str | None = None
    synthetic: bool = True
    replies: int = 0
    reposts: int = 0
    likes: int = 0


class PageOut(BaseModel, Generic[T]):
    total: int
    limit: int
    offset: int
    items: list[T]

class EventDetailOut(EventOut):
    linked_posts: int
    raw: dict
"""Offline smoke test: normalizers + API on a throwaway SQLite DB. Run: python -m pytest test_api.py  (or python test_api.py)"""
import os
import tempfile
from datetime import datetime

os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(tempfile.mkdtemp(), "test.db")

from fastapi.testclient import TestClient  # noqa: E402

from app.db import SessionLocal  # noqa: E402
from app.ingest import _save, normalize_acled, normalize_gdelt  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Persona, Post, Run  # noqa: E402

GDELT_ROW = ["1234567", "20250312"] + [""] * 59
GDELT_ROW[6], GDELT_ROW[16], GDELT_ROW[26], GDELT_ROW[28] = "PROTESTER", "GOVERNMENT", "141", "14"
GDELT_ROW[34], GDELT_ROW[52], GDELT_ROW[53], GDELT_ROW[56], GDELT_ROW[57] = "-3.2", "Miami, Florida, United States", "US", "25.77", "-80.19"
GDELT_ROW[60] = "https://example.com/story"

ACLED_REC = {"event_id_cnty": "USA1001", "event_date": "2025-03-12", "event_type": "Protests",
             "sub_event_type": "Peaceful protest", "actor1": "Protesters (United States)", "country": "United States",
             "location": "Miami", "admin1": "Florida", "latitude": "25.77", "longitude": "-80.19", "fatalities": "0"}


def test_all():
    g, a = normalize_gdelt(GDELT_ROW), normalize_acled(ACLED_REC)
    assert (g.id, g.event_type, g.lat, g.tone) == ("GDELT-1234567", "Protest", 25.77, -3.2)
    assert (a.id, a.location, a.fatalities) == ("ACLED-USA1001", "Miami, Florida", 0)

    with SessionLocal() as s:
        assert _save(s, [g, a]) == 2
        assert _save(s, [normalize_gdelt(GDELT_ROW)]) == 1  # re-ingest must not duplicate
        s.add_all([Run(id=1, seed=4821), Persona(id="P1", name="Rosa Delmar", handle="rosad_cs", persona_type="Local resident")])
        s.flush()
        s.add(Post(id="PST-000001", run_id=1, persona_id="P1", event_id="ACLED-USA1001", narrative="#FareFairness",
                   text="sample", sim_time=datetime(2025, 3, 12, 14, 2)))
        s.commit()

    c = TestClient(app)
    assert c.get("/health").json() == {"status": "ok"}
    assert c.get("/events").json()["total"] == 2
    assert c.get("/events", params={"source": "acled"}).json()["items"][0]["id"] == "ACLED-USA1001"
    assert c.get("/events/ACLED-USA1001").json()["linked_posts"] == 1
    assert c.get("/events/nope").status_code == 404
    assert c.get("/posts", params={"persona_type": "Local resident"}).json()[0]["persona"]["handle"] == "rosad_cs"
    assert c.post("/ingest/acled", json={"country": "United States", "start": "2025-03-01", "end": "2025-03-30"}).status_code == 400


if __name__ == "__main__":
    test_all()
    print("ok")

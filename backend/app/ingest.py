"""Pull events from GDELT and ACLED and normalize them into the events table."""
import csv
import io
import json
import os
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime

from sqlalchemy.orm import Session

from .models import Event

GDELT_BASE = "http://data.gdeltproject.org/gdeltv2"
ACLED_TOKEN_URL = "https://acleddata.com/oauth/token"
ACLED_READ_URL = "https://acleddata.com/api/acled/read"

# CAMEO root codes -> readable event type
CAMEO_ROOT = {
    "01": "Public statement", "02": "Appeal", "03": "Intent to cooperate", "04": "Consult",
    "05": "Diplomatic cooperation", "06": "Material cooperation", "07": "Provide aid", "08": "Yield",
    "09": "Investigate", "10": "Demand", "11": "Disapprove", "12": "Reject", "13": "Threaten",
    "14": "Protest", "15": "Exhibit force posture", "16": "Reduce relations", "17": "Coerce",
    "18": "Assault", "19": "Fight", "20": "Mass violence",
}


def _get(url, headers=None, data=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "overseer-ingest", **(headers or {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def _float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _save(session: Session, events):
    # merge = insert or update by primary key, so re-running an ingest never duplicates
    for e in events:
        session.merge(e)
    session.commit()
    return len(events)


# ---------- GDELT 2.0 Event export (15-minute CSV files, no key needed) ----------

def normalize_gdelt(row):
    """row = one tab-separated line of a GDELT 2.0 export file (61 columns)."""
    return Event(
        id=f"GDELT-{row[0]}", source="gdelt", source_id=row[0],
        event_date=datetime.strptime(row[1], "%Y%m%d").date(),
        event_type=CAMEO_ROOT.get(row[28], row[28]), sub_event_type=row[26],
        actor1=row[6] or None, actor2=row[16] or None,
        country=row[53] or None, location=row[52] or None,
        lat=_float(row[56]), lon=_float(row[57]),
        tone=_float(row[34]), source_url=row[60] or None,
        raw={"cols": row},
    )


def ingest_gdelt(session: Session, timestamp: str | None = None, country: str | None = None, root_codes=None):
    """timestamp: YYYYMMDDHHMMSS on a 15-min boundary; latest file if omitted.
    country: FIPS code (e.g. 'US'). root_codes: e.g. ['14'] for protests only."""
    if timestamp:
        url = f"{GDELT_BASE}/{timestamp}.export.CSV.zip"
    else:
        url = _get(f"{GDELT_BASE}/lastupdate.txt").decode().split("\n")[0].split()[-1]
    # ponytail: one 15-min file per call; a 30-day replay is ~2,880 files -> loop or use BigQuery for bulk backfill
    with zipfile.ZipFile(io.BytesIO(_get(url))) as z:
        text = z.read(z.namelist()[0]).decode("utf-8", errors="replace")
    events = []
    for row in csv.reader(io.StringIO(text), delimiter="\t"):
        if len(row) < 61:
            continue
        if country and row[53] != country:
            continue
        if root_codes and row[28] not in root_codes:
            continue
        events.append(normalize_gdelt(row))
    return _save(session, events)


# ---------- ACLED (OAuth API, needs a registered account) ----------

def normalize_acled(rec):
    return Event(
        id=f"ACLED-{rec['event_id_cnty']}", source="acled", source_id=rec["event_id_cnty"],
        event_date=datetime.strptime(rec["event_date"], "%Y-%m-%d").date(),
        event_type=rec.get("event_type"), sub_event_type=rec.get("sub_event_type"),
        actor1=rec.get("actor1") or None, actor2=rec.get("actor2") or None,
        country=rec.get("country"), location=", ".join(x for x in (rec.get("location"), rec.get("admin1")) if x) or None,
        lat=_float(rec.get("latitude")), lon=_float(rec.get("longitude")),
        fatalities=int(rec["fatalities"]) if str(rec.get("fatalities", "")).isdigit() else None,
        source_url=None, notes=rec.get("notes"),
        raw=rec,
    )


def _acled_token():
    user, pw = os.getenv("ACLED_USERNAME"), os.getenv("ACLED_PASSWORD")
    if not (user and pw):
        raise RuntimeError("Set ACLED_USERNAME and ACLED_PASSWORD (your acleddata.com login) in the environment")
    body = urllib.parse.urlencode({"username": user, "password": pw, "grant_type": "password", "client_id": "acled"}).encode()
    return json.loads(_get(ACLED_TOKEN_URL, data=body))["access_token"]


def ingest_acled(session: Session, country: str, start: str, end: str, limit: int = 5000):
    """start/end: YYYY-MM-DD. Pages through results until exhausted or `limit` reached."""
    token = _acled_token()
    events, page = [], 1
    while len(events) < limit:
        q = urllib.parse.urlencode({
            "_format": "json", "country": country, "event_date": f"{start}|{end}",
            "event_date_where": "BETWEEN", "limit": 500, "page": page,
        })
        data = json.loads(_get(f"{ACLED_READ_URL}?{q}", headers={"Authorization": f"Bearer {token}"})).get("data", [])
        if not data:
            break
        events += [normalize_acled(r) for r in data]
        page += 1
    return _save(session, events[:limit])

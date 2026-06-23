from fastapi import FastAPI
from fastapi import APIRouter
from db.connection import get_connection

router = APIRouter()

@router.get("/api/events")
def get_events():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
                SELECT
                    events.id,
                    events.title,
                    events.starts_at,
                    events.ends_at,
                    venues.name
                FROM events
                JOIN venues ON events.venue_id = venues.id
                ORDER BY "starts_at" ASC
                """
                )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    events = [
        {
            "id": row[0],
            "title": row[1],
            "starts_at": row[2].isoformat(),
            "ends_at": row[3].isoformat(),
            "location": row[4],
        }
        for row in rows
    ]

    return {"events": events}

# #{
#   "events": [
#     {
#       "id": 1,
#       "title": "Leeds Tech Meetup – June Edition",
#       "starts_at": "2026-06-18T18:30:00+01:00",
#       "ends_at": "2026-06-18T21:00:00+01:00",
#       "location": "Nexus, Leeds, LS2 8PD"
#     },
#   // ...
#   ]
# }
# Requirements
# Returns all events from the database
# Results must be ordered — choose an attribute that produces a meaningful and predictable order, and be prepared to justify your decision
# The response body must be an object with an events key, not a bare array
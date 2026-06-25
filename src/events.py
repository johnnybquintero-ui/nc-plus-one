from fastapi import APIRouter, HTTPException
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
        "id": row["id"],
        "title": row["title"],
        "starts_at": row["starts_at"].isoformat(),
        "ends_at": row["ends_at"].isoformat(),
        "location": row["name"],
    }
    for row in rows
]

    return {"events": events}

@router.get("/api/events/{event_id}")
def get_event(event_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
                SELECT
                    events.id,
                    events.title,
                    events.description,
                    events.starts_at,
                    events.ends_at,
                    venues.name,
                    venues.address,
                    venues.capacity,
                    events.created_at
                FROM events
                JOIN venues ON events.venue_id = venues.id
                WHERE events.id = %s
                """,
                (event_id,)
                )
    row = cur.fetchone()

    cur.close()
    conn.close()

    if row is None:
        raise HTTPException(
        status_code = 404,
        detail={"code": "NOT_FOUND", "message": "Event not found"},
    )

    event = {
    "id": row["id"],
    "title": row["title"],
    "description": row["description"],
    "starts_at": row["starts_at"].isoformat(),
    "ends_at": row["ends_at"].isoformat(),
    "location": row["name"],
    "address": row["address"],
    "capacity": row["capacity"],
    "created_at": row["created_at"].isoformat(),
}

    return {"event": event}

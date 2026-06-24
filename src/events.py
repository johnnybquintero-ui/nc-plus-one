from fastapi import FastAPI
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
            "id": row[0],
            "title": row[1],
            "starts_at": row[2].isoformat(),
            "ends_at": row[3].isoformat(),
            "location": row[4],
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

    event ={
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "starts_at": row[3].isoformat(),
            "ends_at": row[4].isoformat(),
            "location": row[5],
            "address": row[6],
            "capacity": row[7],
            "created_at": row[8].isoformat(),
        }

    return {"event": event}

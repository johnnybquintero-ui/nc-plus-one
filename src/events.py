from fastapi import APIRouter, HTTPException, Depends
from src.auth import get_current_user_id
from db.connection import get_connection
from src.schemas import CreateEventRequest, UpdateEventRequest
from pydantic import ValidationError

router = APIRouter()

def updated_value(new_value, existing_value):
    """Return the new value if supplied, otherwise keep the existing value."""
    return new_value if new_value is not None else existing_value

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

@router.post("/api/events", status_code=201)
def create_event(
    payload: dict,
    current_user_id: int = Depends(get_current_user_id),
):
    try:
        payload = CreateEventRequest(**payload)
    except ValidationError:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "BAD_REQUEST",
                "message": "Malformed request body or missing required fields",
            },
        )
    
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute ("""
                INSERT INTO events (
                    title,
                    description,
                    starts_at,
                    ends_at,
                    venue_id,
                    organiser_id
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING
                    id,
                    title,
                    description,
                    starts_at,
                    ends_at,
                    venue_id,
                    organiser_id,
                    created_at
                """,
                (
                    payload.title,
                    payload.description,
                    payload.starts_at,
                    payload.ends_at,
                    payload.venue_id,
                    current_user_id,  
                )
        )

        event = cur.fetchone()
        conn.commit()

    return {"event": event}

@router.patch("/api/events/{event_id}", status_code=200)
def update_event(
    event_id: int,
    payload: dict,
    current_user_id: int = Depends(get_current_user_id),
):
    try:
        payload = UpdateEventRequest(**payload)
    except ValidationError:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "BAD_REQUEST",
                "message": "Invalid request body or date format",
            },
        )

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM events
                WHERE id = %s
                """,
                (event_id,),
            )

            existing_event = cur.fetchone()

            if existing_event is None:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "code": "NOT_FOUND",
                        "message": "Event not found",
                    },
                )

            if existing_event["organiser_id"] != current_user_id:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "code": "FORBIDDEN",
                        "message": "You are not authorised to update this event",
                    },
                )

            new_title = updated_value(
                payload.title,
                existing_event["title"],
            )

            new_description = updated_value(
                payload.description,
                existing_event["description"],
            )

            new_starts_at = updated_value(
                payload.starts_at,
                existing_event["starts_at"],
            )

            new_ends_at = updated_value(
                payload.ends_at,
                existing_event["ends_at"],
            )

            new_venue_id = updated_value(
                payload.venue_id,
                existing_event["venue_id"],
            )

            if new_ends_at <= new_starts_at:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "INVALID_DATE_RANGE",
                        "message": "ends_at must be after starts_at",
                    },
                )

            cur.execute(
                """
                UPDATE events
                SET
                    title = %s,
                    description = %s,
                    starts_at = %s,
                    ends_at = %s,
                    venue_id = %s
                WHERE id = %s
                RETURNING
                    id,
                    title,
                    description,
                    starts_at,
                    ends_at,
                    venue_id,
                    organiser_id,
                    created_at
                """,
                (
                    new_title,
                    new_description,
                    new_starts_at,
                    new_ends_at,
                    new_venue_id,
                    event_id,
                ),
            )

            event = cur.fetchone()

        conn.commit()

        return {"event": event}

    finally:
        conn.close()
    
@router.get("/api/events/{event_id}/attendees")
def get_event_attendees(
    event_id: int,
    current_user_id: int = Depends(get_current_user_id),
):
    conn = get_connection()
    cur = conn.cursor()

    #Get the event
    cur.execute("""
                SELECT *
                FROM events
                WHERE id = %s
                """,
                (event_id,)
                )
    event = cur.fetchone()

    #Check if the event exists
    if event is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NOT_FOUND",
                "message": "Event not found",
            },
        )

    #Verify that the organiser of the event is the same as the current user
    if event["organiser_id"] != current_user_id:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "FORBIDDEN",
                "message": "You are not authorised to view the attendees of this event",
            },
        )

    cur.execute("""
                SELECT
                    rsvps.attendee_id,
                    users.email,
                    users.name
                FROM rsvps
                JOIN users ON rsvps.attendee_id = users.id
                WHERE rsvps.event_id = %s
                """,
                (event_id,)
                )
    
    rows = cur.fetchall()

    cur.close()
    conn.close()

    attendees  = [
        {
            "id": row["attendee_id"],
            "email": row["email"],
            "name": row["name"],
        }
        for row in rows
    ]

    return {"attendees": attendees}
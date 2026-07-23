from fastapi import HTTPException, APIRouter, Depends
from src.auth import get_current_user_id
from db.connection import get_connection

router = APIRouter()

def get_event_by_id(event_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM events
                WHERE id = %s
                """,
                (event_id,),
            )

            return cur.fetchone()
    
def get_rsvp(attendee_id: int, event_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM rsvps
                WHERE attendee_id = %s
                  AND event_id = %s
                """,
                (attendee_id, event_id),
            )

            return cur.fetchone()

@router.post("/api/events/{event_id}/rsvp", status_code=201)
def create_rsvp(
    event_id: int,
    current_user_id: int = Depends(get_current_user_id),
):
    event = get_event_by_id(event_id)

    if not event:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NOT_FOUND",
                "message": "Event not found",
            },
        )
    
    existing_rsvp = get_rsvp(current_user_id, event_id)

    if existing_rsvp:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "CONFLICT",
                "message": "User has already RSVPed to this event",
            },
        )

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO rsvps (
                    attendee_id,
                    event_id
                )
                VALUES (%s, %s)
                RETURNING
                    id,
                    attendee_id,
                    event_id,
                    created_at
                """,
                (
                    current_user_id,
                    event_id,
                ),
            )

            rsvp = cur.fetchone()

        conn.commit()

    return {"rsvp": rsvp}

@router.delete("/api/events/{event_id}/rsvp/me", status_code=204)
def delete_rsvp(
    event_id: int,
    current_user_id: int = Depends(get_current_user_id),
):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM rsvps
                WHERE event_id = %s
                  AND attendee_id = %s
                """,
                (event_id, current_user_id),
            )

            if cur.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "code": "NOT_FOUND",
                        "message": "RSVP not found",
                    },
                )

        conn.commit()
        
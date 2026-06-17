import psycopg2
from connection import connection
import json

def load_users():
    with open("db/data/users.json", "r") as file:
        return json.load(file)

def load_venues():
    with open("db/data/venues.json", "r") as file:
        return json.load(file)

def load_events():
    with open("db/data/events.json", "r") as file:
        return json.load(file)





def drop_users_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS users;")


def create_users_table(cursor):
    cursor.execute("""
            CREATE TABLE users(
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
    

def insert_users(cursor, users):
    for user in users:
        cursor.execute("""
            INSERT INTO users (email, password, name)
            VALUES (%s, %s, %s);
            """,
            (user["email"], user["password"], user["name"])
        )





def drop_venues_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS venues;")

def create_venues_table(cursor):
    cursor.execute("""
            CREATE TABLE venues(
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                address TEXT,
                capacity INT
            );
        """)

def insert_venues(cursor, venues):
    for venue in venues:
        cursor.execute("""
            INSERT INTO venues(name, address, capacity)
            VALUES (%s, %s, %s);
            """,
            (venue["name"], venue["address"], venue["capacity"])
        )





def drop_events_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS events;")

def create_events_table(cursor):
    cursor.execute("""
            CREATE TABLE events(
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description VARCHAR(255),
                starts_at TIMESTAMPTZ NOT NULL,
                ends_at TIMESTAMPTZ NOT NULL,
                organiser_id INT REFERENCES users(id),
                venue_id INT REFERENCES venues(id),
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)

def insert_events(cursor, events):
    for event in events:
        cursor.execute("""
            INSERT INTO events(title, description, starts_at, ends_at, organiser_id, venue_id)
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (event["title"], event["description"], event["starts_at"], event["ends_at"], event["organiser_id"], event["venue_id"])
        )

def seed():
    cursor = connection.cursor()

    drop_events_table(cursor)
    drop_users_table(cursor)
    drop_venues_table(cursor)

    create_users_table(cursor)
    create_venues_table(cursor)
    create_events_table(cursor)

    users = load_users()
    insert_users(cursor, users)

    venues = load_venues()
    insert_venues(cursor, venues)

    events = load_events()
    insert_events(cursor, events)
    
    connection.commit()
    cursor.close()
    connection.close()


if __name__ == "__main__":
    seed()

import psycopg2
from connection import connection
import json

def load_users():
    with open("db/data/users.json", "r") as file:
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
        cursor.execute(
            """
            INSERT INTO users (email, password, name)
            VALUES (%s, %s, %s);
            """,
            (user["email"], user["password"], user["name"])
        )


def seed():
    cursor = connection.cursor()

    drop_users_table(cursor)
    create_users_table(cursor)

    users = load_users()
    insert_users(cursor, users)
    
    
    connection.commit()
    cursor.close()
    connection.close()

if __name__ == "__main__":
    seed()

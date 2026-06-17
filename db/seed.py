import psycopg2
from connection import connection

def seed():
    cursor = connection.cursor()

    print("Connection successful!")

    cursor.close()
    connection.close()

if __name__ == "__main__":
    seed()
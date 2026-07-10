import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

HOST = os.environ["PGHOST"]
PORT = os.environ["PGPORT"]
DATABASE = os.environ["PGDATABASE"]
USER = os.environ["PGUSER"]
PASSWORD = os.environ["PGPASSWORD"]

def get_connection():
    return psycopg2.connect(
        host=HOST,
        port=PORT,
        dbname=DATABASE,
        user=USER,
        password=PASSWORD,
        cursor_factory=RealDictCursor,
    )
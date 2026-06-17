import psycopg2
from credentials import dbname

connection = psycopg2.connect(dbname=dbname)
import psycopg2
from datetime import datetime

DB_RESULTS  = "snake_scores"
DB_USER     = "postgres"
DB_PASSWORD = ""
DB_HOST     = "localhost"
DB_PORT     = "5432"

conn = psycopg2.connect(
    dbname=DB_RESULTS,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

cur.execute(
    "SELECT username, score, level, saved_at "
    "FROM results "
    "ORDER BY score DESC, saved_at ASC"
)
rows = cur.fetchall()

if rows:
    header = f"{'Username':<20}{'Score':<8}{'Level':<8}{'Saved At'}"
    print(header)
    print('-' * len(header))
    for username, score, level, saved_at in rows:
        print(f"{username:<20}{score:<8}{level:<8}{saved_at}")
else:
    print("No results found in the database.")

cur.close()
conn.close()

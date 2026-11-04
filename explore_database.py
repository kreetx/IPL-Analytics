
import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

dsn = oracledb.makedsn(
    os.getenv("DB_HOST"),
    int(os.getenv("DB_PORT")),
    service_name=os.getenv("DB_SERVICE")
)

conn = oracledb.connect(
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    dsn=dsn
)

cursor = conn.cursor()

tables = [
    "MATCHES",
    "PLAYERS",
    "PLAYER_MATCH_STATS",
    "PLAYER_TEAM_SEASONS",
    "TEAMS"
]

for table in tables:
    print("\n" + "=" * 50)
    print("TABLE:", table)

    cursor.execute(f"SELECT * FROM {table} WHERE ROWNUM <= 5")

    columns = [col[0] for col in cursor.description]
    print("COLUMNS:", columns)

    for row in cursor.fetchall():
        print(row)

cursor.close()
conn.close()

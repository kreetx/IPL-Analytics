print("Starting Oracle connection...")
import oracledb
import os
from dotenv import load_dotenv

# Load database credentials
load_dotenv()

try:
    # Get credentials
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = int(os.getenv("DB_PORT"))
    service = os.getenv("DB_SERVICE")

    # Create database connection
    dsn = oracledb.makedsn(
        host,
        port,
        service_name=service
    )

    connection = oracledb.connect(
        user=username,
        password=password,
        dsn=dsn
    )

    print("Connected to Oracle Database!")

    # Check available tables
    cursor = connection.cursor()

    cursor.execute("""
        SELECT table_name
        FROM user_tables
        ORDER BY table_name
    """)

    print("\nIPL DATABASE TABLES:")

    for row in cursor:
        print(row[0])

    cursor.close()
    connection.close()

except Exception as e:
    print("Connection failed!")
    print(e)

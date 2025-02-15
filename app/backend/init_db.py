import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def init_database():
    conn = psycopg2.connect(
        user="postgres",
        password="password",
        host="localhost",
        port="5432"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    try:
        cursor.execute("CREATE DATABASE xackaton_db")
        print("Database created successfully")
    except psycopg2.Error as e:
        print(f"Database already exists: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    init_database()
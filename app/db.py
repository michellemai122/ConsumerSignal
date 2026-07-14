import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "startup_intelligence.db"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def get_connection():
    # Make sure the project directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """
    Creates or resets the SQLite database using sql/schema.sql
    """
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

    conn = get_connection()

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn.executescript(schema_sql)
    conn.commit()
    conn.close()

    print(f"Database initialized at {DB_PATH}")


def run_query(query, params=None, fetch=True):
    """
    Runs a SQL query safely.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if params is None:
        params = ()

    cursor.execute(query, params)

    if fetch:
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    conn.commit()
    conn.close()
    return None
# db.py
import pyodbc
from config import PRODUCT_DB_CONN


# -------------------------------
# Database Connection Functions
# -------------------------------
def get_conn():
    """
    Get a pyodbc connection using the PRODUCT_DB_CONN string from config.
    """
    if not PRODUCT_DB_CONN:
        raise Exception("Set PRODUCT_DB_CONN environment variable in config")
    return pyodbc.connect(PRODUCT_DB_CONN, autocommit=False)


def fetchall_dict(cursor):
    """
    Convert cursor results to a list of dictionaries.

    Example:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Table")
        rows = fetchall_dict(cursor)
    """
    cols = [column[0] for column in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


# -------------------------------
# Optional test block
# -------------------------------
if __name__ == "__main__":
    # Quick test if pyodbc is working and connection can be made
    try:
        conn = get_conn()
        print("Database connection successful!")
        conn.close()
    except Exception as e:
        print("Database connection failed:", e)

import mysql.connector
from mysql.connector import Error
from config import Config

def get_db_connection():
    """
    Establishes and returns a connection to the MySQL database.
    Raises mysql.connector.Error if connection fails.
    """
    connection = mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        charset='utf8mb4',
        use_pure=True
    )
    return connection

def check_db_connection():
    """
    Checks if the MySQL database is reachable and returns (is_connected, error_message).
    """
    try:
        conn = get_db_connection()
        if conn.is_connected():
            conn.close()
            return True, None
    except Error as e:
        return False, str(e)
    return False, "Unknown connection error"

def query_all(query, params=None):
    """
    Executes a SELECT query and returns all matching rows as a list of dictionaries.
    Uses parameterized queries to prevent SQL injection.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        return results
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def query_one(query, params=None):
    """
    Executes a SELECT query and returns a single matching row as a dictionary.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        result = cursor.fetchone()
        return result
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def execute_query(query, params=None, commit=True):
    """
    Executes an INSERT, UPDATE, or DELETE query.
    Returns a dictionary containing 'lastrowid' and 'rowcount'.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        if commit:
            conn.commit()
        return {
            'lastrowid': cursor.lastrowid,
            'rowcount': cursor.rowcount
        }
    except Error as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

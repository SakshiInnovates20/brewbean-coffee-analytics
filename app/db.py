import pymysql
from pymysql.cursors import DictCursor
from flask import current_app

def get_db_connection():
    """
    Establishes and returns a PyMySQL database connection based on Flask config.
    Returns dictionary cursors for easy JSON serialization.
    """
    connection = pymysql.connect(
        host=current_app.config['DB_HOST'],
        port=current_app.config['DB_PORT'],
        user=current_app.config['DB_USER'],
        password=current_app.config['DB_PASSWORD'],
        database=current_app.config['DB_NAME'],
        cursorclass=DictCursor,
        connect_timeout=3
    )
    return connection

def check_db_connection():
    """
    Tests MySQL database connectivity.
    Returns a status dict indicating success or error details without throwing unhandled exceptions.
    """
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 AS alive;")
            result = cursor.fetchone()
        connection.close()
        
        return {
            "connected": True,
            "message": "Database connection successful",
            "host": current_app.config['DB_HOST'],
            "port": current_app.config['DB_PORT'],
            "database": current_app.config['DB_NAME']
        }
    except Exception as e:
        return {
            "connected": False,
            "message": "Failed to connect to MySQL database",
            "error": str(e),
            "host": current_app.config['DB_HOST'],
            "port": current_app.config['DB_PORT'],
            "database": current_app.config['DB_NAME']
        }

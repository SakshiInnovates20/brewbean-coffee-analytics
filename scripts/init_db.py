"""
BrewBean Coffee Analytics System — Database Initialization Utility
Executes schema.sql and seed.sql against the configured MySQL database safely.
"""

import os
import sys
from pathlib import Path
import pymysql
from dotenv import load_dotenv

# Ensure project root is in sys.path and load environment variables
basedir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(basedir))

env_file = basedir / '.env'
load_dotenv(dotenv_path=env_file, override=True)

# DB Credentials from environment variables
DB_HOST = os.environ.get('DB_HOST', '127.0.0.1').strip()
DB_PORT = int(str(os.environ.get('DB_PORT', 3306)).strip())
DB_USER = os.environ.get('DB_USER', 'root').strip()
DB_PASSWORD = os.environ.get('DB_PASSWORD', '').strip()
DB_NAME = os.environ.get('DB_NAME', 'brewbean_analytics').strip()

def execute_sql_file(connection, file_path):
    """
    Executes multiple SQL statements from a file cleanly.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Split by semicolon while ignoring comments
    statements = []
    current = []
    for line in sql_content.splitlines():
        # Remove inline comments starting with --
        clean_line = line.split('--')[0].strip()
        if not clean_line:
            continue
        current.append(clean_line)
        if clean_line.endswith(';'):
            statements.append(' '.join(current))
            current = []

    with connection.cursor() as cursor:
        for stmt in statements:
            if stmt.strip():
                cursor.execute(stmt)
    connection.commit()

def initialize_database():
    """
    Initializes the database schema and populates initial seed data.
    """
    print("==================================================")
    print("  BrewBean Database Initialization")
    print(f"  Target Host: {DB_HOST}:{DB_PORT}")
    print(f"  Target DB  : {DB_NAME}")
    print("==================================================")

    try:
        # Step 1: Connect to MySQL Server (without selecting specific DB first to ensure DB exists)
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            autocommit=True,
            connect_timeout=5
        )
        
        # Create database if not exists
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            cursor.execute(f"USE `{DB_NAME}`;")

        schema_file = basedir / 'database' / 'schema.sql'
        seed_file = basedir / 'database' / 'seed.sql'

        print(f"1. Executing Schema: {schema_file.name}...")
        execute_sql_file(connection, schema_file)
        print("   -> Schema created successfully.")

        print(f"2. Executing Seed Data: {seed_file.name}...")
        execute_sql_file(connection, seed_file)
        print("   -> Seed data inserted successfully.")

        # Step 2: Verify record counts
        print("--------------------------------------------------")
        print("  Database Record Verification Counts:")
        print("--------------------------------------------------")
        
        tables = [
            'franchises', 'shops', 'product_categories', 
            'products', 'customers', 'marketing_campaigns', 
            'sales', 'sale_items'
        ]
        
        with connection.cursor() as cursor:
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) AS total FROM `{table}`;")
                count = cursor.fetchone()[0]
                print(f"  - Table `{table}`: {count} row(s)")
                
        connection.close()
        print("==================================================")
        print("  [SUCCESS] Database Initialization Completed Successfully!")
        print("==================================================")

    except pymysql.Error as err:
        print(f"[ERROR] Database Error: {err}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Initialization Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    initialize_database()

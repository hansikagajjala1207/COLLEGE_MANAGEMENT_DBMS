"""
Database Setup & Initialization Utility
Reads schema.sql and seed.sql and initializes the MySQL database.
Usage:
    python setup_database.py
    python setup_database.py --password your_mysql_password
"""

import os
import sys
import re
import argparse
import mysql.connector
from config import Config

def run_sql_script(cursor, filepath):
    """Executes multi-statement SQL script file safely by stripping comments."""
    print(f"[*] Executing SQL script: {os.path.basename(filepath)}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        sql_commands = f.read()

    # Remove comment lines starting with --
    cleaned_sql = re.sub(r'--[^\n]*', '', sql_commands)

    # Split into individual SQL statements by semicolon
    raw_statements = cleaned_sql.split(';')
    executed_count = 0
    for statement in raw_statements:
        stmt = statement.strip()
        if stmt:
            cursor.execute(stmt)
            executed_count += 1
    print(f"[+] Successfully executed {executed_count} statements from {os.path.basename(filepath)}.")

def init_db(host, port, user, password, db_name):
    """Connects to MySQL server, creates database and executes schema + seed."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    schema_file = os.path.join(base_dir, 'database', 'schema.sql')
    seed_file = os.path.join(base_dir, 'database', 'seed.sql')

    print(f"Connecting to MySQL server at {host}:{port} as user '{user}'...")
    try:
        # Connect to MySQL server without specifying database first
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4',
            use_pure=True
        )
        cursor = conn.cursor()

        print(f"[*] Creating database '{db_name}' if it does not exist...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`;")
        cursor.execute(f"USE `{db_name}`;")

        # Execute schema
        run_sql_script(cursor, schema_file)

        # Execute seed data
        run_sql_script(cursor, seed_file)

        conn.commit()
        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print(" [SUCCESS] Database initialized and seeded successfully!")
        print(" Database Name: student_college_management")
        print(" Admin Login  : username='admin', password='admin123'")
        print("=" * 60)
        return True

    except mysql.connector.Error as err:
        print(f"\n[ERROR] Failed to initialize database: {err.msg}")
        print("Please check your MySQL username and password in .env or pass --password <pwd>.")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Initialize Student College Management MySQL Database")
    parser.add_argument('--host', default=Config.DB_HOST, help="MySQL Host (default: localhost)")
    parser.add_argument('--port', type=int, default=Config.DB_PORT, help="MySQL Port (default: 3306)")
    parser.add_argument('--user', default=Config.DB_USER, help="MySQL User (default: root)")
    parser.add_argument('--password', default=Config.DB_PASSWORD, help="MySQL Password")
    parser.add_argument('--db', default=Config.DB_NAME, help="Database Name (default: student_college_management)")

    args = parser.parse_args()
    success = init_db(args.host, args.port, args.user, args.password, args.db)
    sys.exit(0 if success else 1)

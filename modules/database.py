# modules/database.py

import sqlite3
from datetime import datetime
import json
import threading

# Use thread-local storage to ensure each thread gets its own connection.
# This is the standard way to handle database connections in multi-threaded apps.
thread_local = threading.local()

def get_db_connection(db_path="data/seo_app_cache.db"):
    """
    Gets a database connection from thread-local storage or creates a new one.
    This ensures that each thread has its own separate, safe connection.
    """
    if not hasattr(thread_local, "conn"):
        # The check_same_thread=False is crucial for Streamlit's architecture.
        thread_local.conn = sqlite3.connect(db_path, check_same_thread=False)
        thread_local.conn.row_factory = sqlite3.Row
    return thread_local.conn

class DatabaseManager:
    """
    A class to manage all interactions with the local SQLite database.
    This acts as a dedicated handler for caching API responses to prevent
    redundant API calls, saving costs and building a local dataset.
    This version is designed to be thread-safe for Streamlit.
    """

    def __init__(self, db_path="data/seo_app_cache.db"):
        """
        Initializes the DatabaseManager.
        The connection itself is managed on a per-thread basis.

        Args:
            db_path (str): The file path for the SQLite database.
        """
        self.db_path = db_path
        self.create_table()

    def create_table(self):
        """
        Creates the 'cache' table if it does not already exist.
        """
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    response_json TEXT NOT NULL,
                    timestamp DATETIME NOT NULL
                )
            """)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def check_cache(self, key):
        """
        Checks the cache for a given key.
        """
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT response_json FROM cache WHERE key = ?", (key,))
            row = cursor.fetchone()

            if row:
                return json.loads(row['response_json'])
            else:
                return None
        except (sqlite3.Error, json.JSONDecodeError) as e:
            print(f"Error checking cache for key '{key}': {e}")
            return None

    def update_cache(self, key, data):
        """
        Inserts or replaces a record in the cache.
        """
        json_data_string = json.dumps(data)
        current_timestamp = datetime.utcnow()

        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO cache (key, response_json, timestamp)
                VALUES (?, ?, ?)
            """, (key, json_data_string, current_timestamp))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating cache for key '{key}': {e}")

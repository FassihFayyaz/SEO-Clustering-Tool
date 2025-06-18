# modules/database.py

import sqlite3
from datetime import datetime, timedelta
import json
import threading

# Use thread-local storage to ensure each thread gets its own connection.
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
    Manages all interactions with the local SQLite database with thread-safety.
    Includes logic for cache age validation and clearing the cache.
    """

    def __init__(self, db_path="data/seo_app_cache.db"):
        """
        Initializes the DatabaseManager.
        The connection itself is managed on a per-thread basis.
        """
        self.db_path = db_path
        self.create_table()

    def create_table(self):
        """Creates the 'cache' table if it does not already exist."""
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    response_json TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def check_cache(self, key, max_age_days=None):
        """
        Checks the cache for a given key, considering its age.

        Args:
            key (str): The unique identifier for the API request.
            max_age_days (int, optional): The maximum age of the cache entry in days.
                                          If 0, always considers cache stale (force refetch).
                                          If None, ignores age and returns data if it exists.
        Returns:
            dict: The parsed JSON data if a valid, non-stale entry is found, otherwise None.
        """
        if max_age_days == 0:
            return None # Always fetch new data if duration is 0 days.

        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT response_json, timestamp FROM cache WHERE key = ?", (key,))
            row = cursor.fetchone()

            if row:
                if max_age_days is not None:
                    timestamp = datetime.fromisoformat(row['timestamp'])
                    if datetime.utcnow() - timestamp > timedelta(days=max_age_days):
                        return None # Cache is stale, return None.
                
                # Cache is not stale or age is not a factor.
                return json.loads(row['response_json'])
            else:
                return None # No entry found.
        except (sqlite3.Error, json.JSONDecodeError, TypeError) as e:
            print(f"Error checking cache for key '{key}': {e}")
            return None

    def update_cache(self, key, data):
        """Inserts or replaces a record in the cache with the current timestamp."""
        json_data_string = json.dumps(data)
        current_timestamp = datetime.utcnow().isoformat()

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

    def clear_all_cache(self):
        """Deletes all records from the cache table."""
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cache")
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error clearing cache: {e}")
            return False


# modules/database.py

import sqlite3
from datetime import datetime
import json

class DatabaseManager:
    """
    A class to manage all interactions with the local SQLite database.
    This acts as a dedicated handler for caching API responses to prevent
    redundant API calls, saving costs and building a local dataset.
    """

    def __init__(self, db_path="data/seo_app_cache.db"):
        """
        Initializes the DatabaseManager and connects to the SQLite database.
        It also ensures the necessary table exists.

        Args:
            db_path (str): The file path for the SQLite database.
        """
        self.db_path = db_path
        self.conn = None
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row # Allows accessing columns by name
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            # In a real GUI app, you'd show this error to the user.
            # For now, we print to the console.
        
        # Ensure the cache table exists every time the manager is initialized.
        self.create_table()

    def create_table(self):
        """
        Creates the 'cache' table if it does not already exist.
        This table will store raw JSON responses from the DataForSEO API.
        """
        if not self.conn:
            return
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    response_json TEXT NOT NULL,
                    timestamp DATETIME NOT NULL
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def check_cache(self, key):
        """
        Checks the cache for a given key.

        Args:
            key (str): A unique identifier for the API request.
                       e.g., "serp|best laptops for college|us|desktop"

        Returns:
            dict: The parsed JSON data if the key is found, otherwise None.
        """
        if not self.conn:
            return None

        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT response_json FROM cache WHERE key = ?", (key,))
            row = cursor.fetchone()

            if row:
                # The data is stored as a JSON string, so we parse it before returning.
                return json.loads(row['response_json'])
            else:
                return None
        except (sqlite3.Error, json.JSONDecodeError) as e:
            print(f"Error checking cache for key '{key}': {e}")
            return None

    def update_cache(self, key, data):
        """
        Inserts or replaces a record in the cache.
        The data is stored as a raw JSON string.

        Args:
            key (str): The unique identifier for the API request.
            data (dict): The complete JSON data (as a Python dictionary) from the API response.
        """
        if not self.conn:
            return

        # We convert the Python dictionary to a JSON string for storage.
        json_data_string = json.dumps(data)
        current_timestamp = datetime.utcnow()

        try:
            cursor = self.conn.cursor()
            # 'INSERT OR REPLACE' is a handy SQLite command that will either
            # insert a new row or replace the existing one if the PRIMARY KEY (key) matches.
            cursor.execute("""
                INSERT OR REPLACE INTO cache (key, response_json, timestamp)
                VALUES (?, ?, ?)
            """, (key, json_data_string, current_timestamp))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating cache for key '{key}': {e}")

    def __del__(self):
        """
        Destructor to ensure the database connection is closed when the object is destroyed.
        """
        if self.conn:
            self.conn.close()


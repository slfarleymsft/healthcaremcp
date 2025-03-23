import sqlite3
import time
from datetime import datetime

class UsageService:
    def __init__(self, db_path="usage.db"):
        """Initialize usage tracking service with anonymous tracking only"""
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create usage table for anonymous session tracking only
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            tool TEXT NOT NULL,
            timestamp REAL NOT NULL,
            api_calls INTEGER NOT NULL DEFAULT 1
        )
        ''')

        conn.commit()
        conn.close()

    def record_usage(self, session_id, tool, api_calls=1):
        """Record API usage for a session anonymously"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO usage (session_id, tool, timestamp, api_calls) VALUES (?, ?, ?, ?)",
            (session_id, tool, time.time(), api_calls)
        )

        conn.commit()
        conn.close()

    def get_monthly_usage(self, session_id, month=None, year=None):
        """Get current month's usage for a session"""
        if month is None:
            month = datetime.now().month
        if year is None:
            year = datetime.now().year

        # Calculate start and end timestamps for the month
        start_date = datetime(year, month, 1).timestamp()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).timestamp()
        else:
            end_date = datetime(year, month + 1, 1).timestamp()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get total API calls for the month
        cursor.execute(
            "SELECT SUM(api_calls) FROM usage WHERE session_id = ? AND timestamp >= ? AND timestamp < ?",
            (session_id, start_date, end_date)
        )
        total_calls = cursor.fetchone()[0] or 0

        # Get tool-specific usage
        cursor.execute(
            "SELECT tool, SUM(api_calls) FROM usage WHERE session_id = ? AND timestamp >= ? AND timestamp < ? GROUP BY tool",
            (session_id, start_date, end_date)
        )
        tool_usage = {tool: count for tool, count in cursor.fetchall()}

        conn.close()

        return {
            "session_id": session_id,
            "month": month,
            "year": year,
            "total_api_calls": total_calls,
            "tool_usage": tool_usage
        }

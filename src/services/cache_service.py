import json
import time
import os
import sqlite3
from pathlib import Path

class CacheService:
    def __init__(self, db_path="cache.db", ttl=3600):  # Default TTL: 1 hour
        """Initialize cache service with SQLite backend"""
        self.db_path = db_path
        self.default_ttl = ttl
        self._init_db()
    
    def _init_db(self):
        """Initialize the SQLite database if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create cache table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            expires_at REAL NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def get(self, key):
        """Get value from cache if it exists and is not expired"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get cache entry
        cursor.execute("SELECT data, expires_at FROM cache WHERE key = ?", (key,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return None
        
        data, expires_at = result
        
        # Check if expired
        if expires_at < time.time():
            cursor.execute("DELETE FROM cache WHERE key = ?", (key,))
            conn.commit()
            conn.close()
            return None
        
        conn.close()
        return json.loads(data)
    
    def set(self, key, value, ttl=None):
        """Set value in cache with optional TTL"""
        ttl = ttl or self.default_ttl
        expires_at = time.time() + ttl
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert or replace cache entry
        cursor.execute(
            "INSERT OR REPLACE INTO cache (key, data, expires_at) VALUES (?, ?, ?)",
            (key, json.dumps(value), expires_at)
        )
        
        conn.commit()
        conn.close()
    
    def delete(self, key):
        """Delete value from cache"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM cache WHERE key = ?", (key,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def clear_expired(self):
        """Clear all expired cache entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM cache WHERE expires_at < ?", (time.time(),))
        deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return deleted

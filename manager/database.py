import sqlite3
import pandas as pd
import datetime
import os

class DatabaseManager:
    def __init__(self, db_name="../data/ranking_data.db"): # パスを修正
        # ...
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS rankings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT,
                target_url TEXT,
                google_rank TEXT,
                google_hits TEXT,
                yahoo_rank TEXT,
                yahoo_hits TEXT,
                check_date TIMESTAMP,
                status TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def save_result(self, data):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        c.execute('''
            INSERT INTO rankings (keyword, target_url, google_rank, google_hits, yahoo_rank, yahoo_hits, check_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data["keyword"],
            data["target_url"],
            data["google_rank"],
            data["google_hits"],
            data["yahoo_rank"],
            data["yahoo_hits"],
            now,
            data["status"]
        ))
        conn.commit()
        conn.close()

    def get_all_data(self):
        conn = sqlite3.connect(self.db_name)
        df = pd.read_sql_query("SELECT * FROM rankings ORDER BY id DESC", conn)
        conn.close()
        return df

    def clear_all_data(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("DELETE FROM rankings")
        conn.commit()
        conn.close()
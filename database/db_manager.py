import sqlite3
import datetime
import os
from contextlib import closing

DB_NAME = 'bot_reinos.db'
SQL_FILE_PATH = os.path.join(os.path.dirname(__file__), 'sql', 'init_db.sql')

def inicializar_db():
    with closing(sqlite3.connect(DB_NAME)) as conn:
        with conn:
            with open(SQL_FILE_PATH, 'r', encoding='utf-8') as f:
                script = f.read()
                conn.executescript(script)
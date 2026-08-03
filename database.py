import sqlite3

def init_db():
    conn = sqlite3.connect("djassa.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS artisans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            metier TEXT NOT NULL,
            commune TEXT NOT NULL,
            description TEXT,
            badge TEXT,
            appel_url TEXT,
            whatsapp_url TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect("djassa.db", check_same_thread=False)
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

def rechercher_artisans_intelligent(query="", commune_filtre=""):
    conn = get_connection()
    cursor = conn.cursor()
    
    sql = "SELECT nom, metier, commune, description, badge, appel_url, whatsapp_url FROM artisans WHERE 1=1"
    params = []
    
    if query:
        sql += " AND (nom LIKE ? OR metier LIKE ? OR description LIKE ?)"
        q = f"%{query}%"
        params.extend([q, q, q])
        
    if commune_filtre and commune_filtre != "Toutes les communes":
        sql += " AND commune LIKE ?"
        params.append(f"%{commune_filtre}%")
        
    cursor.execute(sql, params)
    lignes = cursor.fetchall()
    conn.close()
    
    return [
        {
            "nom": r[0],
            "metier": r[1],
            "commune": r[2],
            "description": r[3],
            "badge": r[4],
            "appel_url": r[5],
            "whatsapp_url": r[6]
        } for r in lignes
    ]
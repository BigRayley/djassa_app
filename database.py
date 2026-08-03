import sqlite3

def init_db():
    conn = sqlite3.connect("djassa.db", check_same_thread=False)
    cursor = conn.cursor()
    
    # 1. Table des artisans
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
    
    # 2. Table des avis
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS avis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artisan_id INTEGER NOT NULL,
            note INTEGER NOT NULL,
            commentaire TEXT,
            FOREIGN KEY (artisan_id) REFERENCES artisans (id)
        )
    """)

    # 3. Table des messages avec support d'images
    cursor.execute("DROP TABLE IF EXISTS messages")
    cursor.execute("""
        CREATE TABLE messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artisan_id INTEGER NOT NULL,
            expediteur TEXT NOT NULL,
            contenu TEXT,
            image_url TEXT,
            date_envoi DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (artisan_id) REFERENCES artisans (id)
        )
    """)
    
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect("djassa.db", check_same_thread=False)

def rechercher_artisans_intelligent(query="", commune_filtre=""):
    conn = get_connection()
    cursor = conn.cursor()
    
    sql = "SELECT id, nom, metier, commune, description, badge, appel_url, whatsapp_url FROM artisans WHERE 1=1"
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
            "id": r[0], "nom": r[1], "metier": r[2], "commune": r[3],
            "description": r[4], "badge": r[5], "appel_url": r[6], "whatsapp_url": r[7]
        } for r in lignes
    ]

def ajouter_avis(artisan_id, note, commentaire):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO avis (artisan_id, note, commentaire) VALUES (?, ?, ?)", (artisan_id, note, commentaire))
    conn.commit()
    conn.close()

def obtenir_avis(artisan_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT note, commentaire FROM avis WHERE artisan_id = ?", (artisan_id,))
    lignes = cursor.fetchall()
    conn.close()
    return [{"note": r[0], "commentaire": r[1]} for r in lignes]

def envoyer_message(artisan_id, expediteur, contenu, image_url=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (artisan_id, expediteur, contenu, image_url) VALUES (?, ?, ?, ?)", (artisan_id, expediteur, contenu, image_url))
    conn.commit()
    conn.close()

def obtenir_messages(artisan_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT expediteur, contenu, image_url, date_envoi FROM messages WHERE artisan_id = ? ORDER BY date_envoi DESC", (artisan_id,))
    lignes = cursor.fetchall()
    conn.close()
    return [{"expediteur": r[0], "contenu": r[1], "image_url": r[2], "date_envoi": r[3]} for r in lignes]
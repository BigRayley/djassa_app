import sqlite3

def init_db():
    conn = sqlite3.connect("djassa.db", check_same_thread=False)
    cursor = conn.cursor()
    
    # 1. Table des artisans (existante)
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
    
    # 2. NOUVEAU : Table des avis
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS avis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artisan_id INTEGER NOT NULL,
            note INTEGER NOT NULL,
            commentaire TEXT,
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
    
    # Attention : j'ai ajouté la récupération de l'ID pour pouvoir lier les avis
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
            "id": r[0],
            "nom": r[1],
            "metier": r[2],
            "commune": r[3],
            "description": r[4],
            "badge": r[5],
            "appel_url": r[6],
            "whatsapp_url": r[7]
        } for r in lignes
    ]

# --- NOUVELLES FONCTIONS POUR LE SYSTÈME DE NOTATION ---

def ajouter_avis(artisan_id, note, commentaire):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO avis (artisan_id, note, commentaire) VALUES (?, ?, ?)", 
        (artisan_id, note, commentaire)
    )
    conn.commit()
    conn.close()

def obtenir_avis(artisan_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT note, commentaire FROM avis WHERE artisan_id = ?", (artisan_id,))
    lignes = cursor.fetchall()
    conn.close()
    return [{"note": r[0], "commentaire": r[1]} for r in lignes]
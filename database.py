def init_db():
    conn = sqlite3.connect("djassa.db", check_same_thread=False)
    cursor = conn.cursor()
    
    # On recrée proprement la table artisans avec les colonnes password, lat, lon
    cursor.execute("DROP TABLE IF EXISTS artisans")
    cursor.execute("""
        CREATE TABLE artisans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            metier TEXT NOT NULL,
            commune TEXT NOT NULL,
            description TEXT,
            badge TEXT,
            appel_url TEXT,
            whatsapp_url TEXT,
            password TEXT DEFAULT '1234',
            lat REAL DEFAULT 5.3600,
            lon REAL DEFAULT -4.0083
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

    # 3. Table des messages
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
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
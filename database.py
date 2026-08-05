def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS artisans (
                id SERIAL PRIMARY KEY,
                nom TEXT,
                metier TEXT,
                commune TEXT,
                description TEXT,
                badge TEXT,
                appel_url TEXT,
                whatsapp_url TEXT,
                password TEXT,
                lat FLOAT DEFAULT 5.3600,
                lon FLOAT DEFAULT -4.0083
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS avis (
                id SERIAL PRIMARY KEY,
                artisan_id INT REFERENCES artisans(id),
                note INT,
                commentaire TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                artisan_id INT REFERENCES artisans(id),
                expediteur TEXT,
                contenu TEXT,
                date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                id SERIAL PRIMARY KEY,
                artisan_id INT REFERENCES artisans(id),
                image_b64 TEXT,
                description TEXT
            );
        """)
        # Table Pharmacies
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pharmacies (
                id SERIAL PRIMARY KEY,
                nom TEXT,
                commune TEXT,
                contact TEXT,
                localisation TEXT,
                garde_active BOOLEAN DEFAULT TRUE
            );
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erreur DB init: {e}")
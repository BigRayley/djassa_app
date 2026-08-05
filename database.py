import psycopg2

def get_connection():
    return psycopg2.connect(
        host="aws-0-eu-west-1.pooler.supabase.com",
        port=6543,
        dbname="postgres",
        user="postgres.twbrxvmizmjbgpxxrdsq",
        password="Armelo0731@"
    )

def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Création des tables si elles n'existent pas
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
                password TEXT DEFAULT '1234',
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
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erreur DB init: {e}")

def ajouter_artisan(nom, metier, commune, description, badge, appel_url, whatsapp_url, password="1234", lat=5.3600, lon=-4.0083):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO artisans (nom, metier, commune, description, badge, appel_url, whatsapp_url, password, lat, lon)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (nom, metier, commune, description, badge, appel_url, whatsapp_url, password, lat, lon))
    conn.commit()
    conn.close()

def rechercher_artisans_intelligent(query="", commune_filtre=""):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "SELECT id, nom, metier, commune, description, badge, appel_url, whatsapp_url, lat, lon FROM artisans WHERE 1=1"
    params = []
    if query:
        sql += " AND (nom ILIKE %s OR metier ILIKE %s OR description ILIKE %s)"
        q = f"%{query}%"
        params.extend([q, q, q])
    if commune_filtre and commune_filtre != "Toutes les communes":
        sql += " AND commune ILIKE %s"
        params.append(f"%{commune_filtre}%")
    cursor.execute(sql, params)
    lignes = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "nom": r[1], "metier": r[2], "commune": r[3], "description": r[4], "badge": r[5], "appel_url": r[6], "whatsapp_url": r[7], "lat": r[8], "lon": r[9]} for r in lignes]

def ajouter_avis(artisan_id, note, commentaire):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO avis (artisan_id, note, commentaire) VALUES (%s, %s, %s)", (artisan_id, note, commentaire))
    conn.commit()
    conn.close()

def obtenir_avis(artisan_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT note, commentaire FROM avis WHERE artisan_id = %s", (artisan_id,))
    lignes = cursor.fetchall()
    conn.close()
    return [{"note": r[0], "commentaire": r[1]} for r in lignes]

def envoyer_message(artisan_id, expediteur, contenu):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (artisan_id, expediteur, contenu) VALUES (%s, %s, %s)", (artisan_id, expediteur, contenu))
    conn.commit()
    conn.close()

def obtenir_messages(artisan_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT expediteur, contenu, date_envoi FROM messages WHERE artisan_id = %s ORDER BY date_envoi ASC", (artisan_id,))
    lignes = cursor.fetchall()
    conn.close()
    return [{"expediteur": r[0], "contenu": r[1], "date_envoi": r[2]} for r in lignes]

def verifier_connexion_artisan(nom_artisan, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nom FROM artisans WHERE nom ILIKE %s AND password = %s", (f"%{nom_artisan}%", password))
    res = cursor.fetchone()
    conn.close()
    return res
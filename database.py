import psycopg2
import hashlib

def crypter_mot_de_passe(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def get_connection():
    try:
        return psycopg2.connect(
            host="aws-0-eu-west-1.pooler.supabase.com",
            port=6543,
            dbname="postgres",
            user="postgres.twbrxvmizmjbgpxxrdsq",
            password="Armelo0731@"
        )
    except Exception as e:
        print(f"Erreur de connexion DB: {e}")
        return None

def init_db():
    conn = get_connection()
    if not conn:
        return
    try:
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
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erreur initialisation tables: {e}")

def ajouter_artisan(nom, metier, commune, description, badge, appel_url, whatsapp_url, password="1234", lat=5.3600, lon=-4.0083):
    conn = get_connection()
    if not conn: return
    try:
        password_crypte = crypter_mot_de_passe(password)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO artisans (nom, metier, commune, description, badge, appel_url, whatsapp_url, password, lat, lon)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nom, metier, commune, description, badge, appel_url, whatsapp_url, password_crypte, lat, lon))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erreur ajout artisan: {e}")

def rechercher_artisans_intelligent(query="", commune_filtre=""):
    conn = get_connection()
    if not conn: return []
    try:
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
        cursor.close()
        conn.close()
        return [{"id": r[0], "nom": r[1], "metier": r[2], "commune": r[3], "description": r[4], "badge": r[5], "appel_url": r[6], "whatsapp_url": r[7], "lat": r[8], "lon": r[9]} for r in lignes]
    except Exception as e:
        print(f"Erreur recherche: {e}")
        return []

def ajouter_avis(artisan_id, note, commentaire):
    conn = get_connection()
    if not conn: return
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO avis (artisan_id, note, commentaire) VALUES (%s, %s, %s)", (artisan_id, note, commentaire))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erreur avis: {e}")

def obtenir_avis(artisan_id):
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT note, commentaire FROM avis WHERE artisan_id = %s", (artisan_id,))
        lignes = cursor.fetchall()
        cursor.close()
        conn.close()
        return [{"note": r[0], "commentaire": r[1]} for r in lignes]
    except Exception as e:
        return []

def obtenir_note_moyenne(artisan_id):
    conn = get_connection()
    if not conn: return 0.0, 0
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT AVG(note), COUNT(id) FROM avis WHERE artisan_id = %s", (artisan_id,))
        res = cursor.fetchone()
        cursor.close()
        conn.close()
        if res and res[0] is not None:
            return round(res[0], 1), res[1]
        return 0.0, 0
    except Exception as e:
        return 0.0, 0

def envoyer_message(artisan_id, expediteur, contenu):
    conn = get_connection()
    if not conn: return
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (artisan_id, expediteur, contenu) VALUES (%s, %s, %s)", (artisan_id, expediteur, contenu))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erreur message: {e}")

def obtenir_messages(artisan_id):
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT expediteur, contenu, date_envoi FROM messages WHERE artisan_id = %s ORDER BY date_envoi ASC", (artisan_id,))
        lignes = cursor.fetchall()
        cursor.close()
        conn.close()
        return [{"expediteur": r[0], "contenu": r[1], "date_envoi": r[2]} for r in lignes]
    except Exception as e:
        return []

def verifier_connexion_artisan(nom_artisan, password):
    conn = get_connection()
    if not conn: return None
    try:
        password_crypte = crypter_mot_de_passe(password)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom FROM artisans WHERE nom ILIKE %s AND password = %s", (f"%{nom_artisan}%", password_crypte))
        res = cursor.fetchone()
        cursor.close()
        conn.close()
        return res
    except Exception as e:
        return None

def ajouter_image_portfolio(artisan_id, image_b64, description=""):
    conn = get_connection()
    if not conn: return
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO portfolio (artisan_id, image_b64, description) VALUES (%s, %s, %s)", (artisan_id, image_b64, description))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erreur portfolio: {e}")

def obtenir_portfolio(artisan_id):
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT image_b64, description FROM portfolio WHERE artisan_id = %s", (artisan_id,))
        lignes = cursor.fetchall()
        cursor.close()
        conn.close()
        return [{"image_b64": r[0], "description": r[1]} for r in lignes]
    except Exception as e:
        return []

def obtenir_toutes_les_stats():
    conn = get_connection()
    if not conn: return 0, 0, 0
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM artisans")
        nb_artisans = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM avis")
        nb_avis = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM messages")
        nb_messages = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return nb_artisans, nb_avis, nb_messages
    except Exception as e:
        return 0, 0, 0

def obtenir_tous_les_artisans_admin():
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom, metier, commune FROM artisans ORDER BY id DESC")
        lignes = cursor.fetchall()
        cursor.close()
        conn.close()
        return [{"id": r[0], "nom": r[1], "metier": r[2], "commune": r[3]} for r in lignes]
    except Exception as e:
        return []

def supprimer_artisan(artisan_id):
    conn = get_connection()
    if not conn: return
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM portfolio WHERE artisan_id = %s", (artisan_id,))
        cursor.execute("DELETE FROM messages WHERE artisan_id = %s", (artisan_id,))
        cursor.execute("DELETE FROM avis WHERE artisan_id = %s", (artisan_id,))
        cursor.execute("DELETE FROM artisans WHERE id = %s", (artisan_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erreur suppression: {e}")

def ajouter_pharmacie(nom, commune, contact, localisation):
    conn = get_connection()
    if not conn: return
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO pharmacies (nom, commune, contact, localisation) VALUES (%s, %s, %s, %s)", (nom, commune, contact, localisation))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erreur pharmacie: {e}")

def obtenir_pharmacies(commune_filtre=""):
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        if commune_filtre and commune_filtre != "Toutes les communes":
            cursor.execute("SELECT nom, commune, contact, localisation FROM pharmacies WHERE garde_active = TRUE AND commune ILIKE %s", (f"%{commune_filtre}%",))
        else:
            cursor.execute("SELECT nom, commune, contact, localisation FROM pharmacies WHERE garde_active = TRUE")
        lignes = cursor.fetchall()
        cursor.close()
        conn.close()
        return [{"nom": r[0], "commune": r[1], "contact": r[2], "localisation": r[3]} for r in lignes]
    except Exception as e:
        return []

def vider_pharmacies():
    conn = get_connection()
    if not conn: return
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pharmacies")
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erreur vider pharmacies: {e}")
import psycopg2

DATABASE_URL = "postgresql://postgres:Armelo0731@@db.twbrxvmizmjbgpxxrdsq.supabase.co:5432/postgres"
def get_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    try:
        conn = get_connection()
        conn.close()
    except Exception as e:
        print(f"Erreur : {e}")

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

def envoyer_message(artisan_id, expediteur, contenu, image_url=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (artisan_id, expediteur, contenu, image_url) VALUES (%s, %s, %s, %s)", (artisan_id, expediteur, contenu, image_url))
    conn.commit()
    conn.close()

def obtenir_messages(artisan_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT expediteur, contenu, image_url, date_envoi FROM messages WHERE artisan_id = %s ORDER BY date_envoi DESC", (artisan_id,))
    lignes = cursor.fetchall()
    conn.close()
    return [{"expediteur": r[0], "contenu": r[1], "image_url": r[2], "date_envoi": r[3]} for r in lignes]

def verifier_connexion_artisan(nom_artisan, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nom FROM artisans WHERE nom ILIKE %s AND password = %s", (f"%{nom_artisan}%", password))
    res = cursor.fetchone()
    conn.close()
    return res
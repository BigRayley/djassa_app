import sqlite3

def get_connection():
    conn = sqlite3.connect("djassa.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table des artisans
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artisans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            commune TEXT NOT NULL,
            service TEXT NOT NULL,
            telephone TEXT,
            description TEXT,
            latitude REAL,
            longitude REAL
        )
    ''')
    
    # Table globale des pharmacies d'Abidjan (avec indicateur "de_garde")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pharmacies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            commune TEXT NOT NULL,
            adresse TEXT NOT NULL,
            telephone TEXT,
            de_garde INTEGER DEFAULT 0
        )
    ''')
    
    # Insertion de données de test pour les artisans si vide
    cursor.execute("SELECT COUNT(*) FROM artisans")
    if cursor.fetchone()[0] == 0:
        donnees_test_artisans = [
            ("Kouassi Plomberie", "Cocody", "Plomberie", "0707070707", "Dépannage rapide, réparation de fuites et tuyauterie.", 5.359952, -3.987597),
            ("Menuiserie Bamba", "Yopougon", "Menuiserie", "0505050505", "Création de meubles sur mesure, portes et réparation.", 5.335040, -4.081590),
            ("Dépannage Auto Pro", "Marcory", "Mécanique", "0101010101", "Mécanicien auto professionnel, diagnostic complet et vidange.", 5.302300, -3.990400),
            ("Électricité Konan", "Abobo", "Électricité", "0909090909", "Installation électrique, dépannage et mise aux normes.", 5.416670, -4.016670)
        ]
        cursor.executemany('''
            INSERT INTO artisans (nom, commune, service, telephone, description, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', donnees_test_artisans)

    # Insertion de données de test pour les pharmacies si vide
    cursor.execute("SELECT COUNT(*) FROM pharmacies")
    if cursor.fetchone()[0] == 0:
        donnees_test_pharmacies = [
            ("Pharmacie des Grâces", "Cocody", "Riviera 2, Boulevard Mitterrand", "2722400000", 1),
            ("Pharmacie du Plateau", "Plateau", "Avenue Chardy, Centre-ville", "2720320000", 0),
            ("Pharmacie Yopougon Niangon", "Yopougon", "Niangon Nord Attoban", "2723450000", 1),
            ("Pharmacie Marcory Zone 4", "Marcory", "Zone 4, Rue Pierre et Marie Curie", "2721350000", 0),
            ("Pharmacie Abobo Gare", "Abobo", "Près de la gare routière", "2724300000", 1)
        ]
        cursor.executemany('''
            INSERT INTO pharmacies (nom, commune, adresse, telephone, de_garde)
            VALUES (?, ?, ?, ?, ?)
        ''', donnees_test_pharmacies)
        
    conn.commit()
    conn.close()

# --- Fonctions Artisans ---
def rechercher_artisans_intelligent(query, commune, service):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "SELECT * FROM artisans WHERE 1=1"
    params = []
    if query:
        sql += " AND (nom LIKE ? OR description LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%"])
    if commune and commune != "Toutes les communes":
        sql += " AND commune = ?"
        params.append(commune)
    if service and service != "Tous les services":
        sql += " AND service = ?"
        params.append(service)
    cursor.execute(sql, params)
    resultats = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return resultats

def ajouter_artisan(nom, commune, service, telephone, description):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO artisans (nom, commune, service, telephone, description, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (nom, commune, service, telephone, description, 5.3600, -4.0083))
    conn.commit()
    conn.close()

def obtenir_tous_artisans():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM artisans")
    resultats = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return resultats

def supprimer_artisan(artisan_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM artisans WHERE id = ?", (artisan_id,))
    conn.commit()
    conn.close()

# --- Fonctions Pharmacies ---
def obtenir_toutes_pharmacies(commune=None, uniquement_garde=False):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "SELECT * FROM pharmacies WHERE 1=1"
    params = []
    
    if commune and commune != "Toutes les communes":
        sql += " AND commune = ?"
        params.append(commune)
        
    if uniquement_garde:
        sql += " AND de_garde = 1"
        
    cursor.execute(sql, params)
    resultats = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return resultats

def basculer_statut_garde(pharmacie_id, nouveau_statut):
    """Permet à l'admin de changer l'état de garde d'une pharmacie (0 ou 1)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE pharmacies SET de_garde = ? WHERE id = ?", (nouveau_statut, pharmacie_id))
    conn.commit()
    conn.close()
import sqlite3

def get_connection():
    # Crée ou se connecte à un fichier de base de données local nommé djassa.db
    conn = sqlite3.connect("djassa.db", check_same_thread=False)
    # Permet d'accéder aux colonnes par leur nom (comme un dictionnaire)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialise la base de données de DJASSA avec la table des artisans."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Création de la table 'artisans' si elle n'existe pas encore
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artisans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            commune TEXT NOT NULL,
            service TEXT NOT NULL,
            telephone TEXT,
            description TEXT
        )
    ''')
    
    # Vérification : si la base est vide, on ajoute des artisans de test
    cursor.execute("SELECT COUNT(*) FROM artisans")
    if cursor.fetchone()[0] == 0:
        donnees_test = [
            ("Kouassi Plomberie", "Cocody", "Plomberie", "0707070707", "Dépannage rapide, réparation de fuites et tuyauterie."),
            ("Menuiserie Bamba", "Yopougon", "Menuiserie", "0505050505", "Création de meubles sur mesure, portes et réparation."),
            ("Dépannage Auto Pro", "Marcory", "Mécanique", "0101010101", "Mécanicien auto professionnel, diagnostic complet et vidange."),
            ("Électricité Konan", "Abobo", "Électricité", "0909090909", "Installation électrique, dépannage et mise aux normes.")
        ]
        cursor.executemany('''
            INSERT INTO artisans (nom, commune, service, telephone, description)
            VALUES (?, ?, ?, ?, ?)
        ''', donnees_test)
        
    conn.commit()
    conn.close()

def rechercher_artisans_intelligent(query, commune, service):
    """Recherche les artisans selon les filtres choisis dans l'interface."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Requête SQL de base
    sql = "SELECT * FROM artisans WHERE 1=1"
    params = []
    
    # Filtre 1 : Le nom ou la description tapé dans la barre de recherche
    if query:
        sql += " AND (nom LIKE ? OR description LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%"])
        
    # Filtre 2 : La commune
    if commune and commune != "Toutes les communes":
        sql += " AND commune = ?"
        params.append(commune)
        
    # Filtre 3 : Le service
    if service and service != "Tous les services":
        sql += " AND service = ?"
        params.append(service)
        
    cursor.execute(sql, params)
    # Transformation des résultats en liste de dictionnaires pour l'affichage dans Streamlit
    resultats = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return resultats
import base64
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from database import get_connection, init_db, rechercher_artisans_intelligent, ajouter_avis, obtenir_avis, envoyer_message, obtenir_messages, verifier_connexion_artisan

# Initialisation de la base de données SQLite
init_db()

st.set_page_config(page_title="DJASSA - Bêta", page_icon="🇨🇮", layout="centered")

# --- CSS PERSONNALISÉ MOBILE FIRST ---
st.markdown("""
    <style>
    .stButton button { width: 100%; border-radius: 8px; font-weight: bold; padding: 10px; }
    div[data-testid="stVerticalBlock"] > div { max-width: 100%; }
    input, textarea { font-size: 16px !important; }
    </style>
""", unsafe_allow_html=True)

def charger_tous_artisans():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nom, metier, commune, description, badge, appel_url, whatsapp_url, lat, lon FROM artisans")
    lignes = cursor.fetchall()
    conn.close()
    return [
        {
            "id": r[0], "nom": r[1], "metier": r[2], "commune": r[3],
            "description": r[4], "badge": r[5], "appel_url": r[6], "whatsapp_url": r[7],
            "lat": r[8], "lon": r[9]
        } for r in lignes
    ]

tous_artisans = charger_tous_artisans()

def calculer_moyenne_avis(avis_list):
    if not avis_list:
        return 0
    total = sum(a['note'] for a in avis_list)
    return round(total / len(avis_list), 1)

# Variables de session
if "utilisateur_pseudo" not in st.session_state:
    st.session_state.utilisateur_pseudo = ""
if "resultats_recherche" not in st.session_state:
    st.session_state.resultats_recherche = None
if "appel_en_cours" not in st.session_state:
    st.session_state.appel_en_cours = None
if "chat_actif_id" not in st.session_state:
    st.session_state.chat_actif_id = None
if "chat_actif_nom" not in st.session_state:
    st.session_state.chat_actif_nom = ""
if "favoris" not in st.session_state:
    st.session_state.favoris = []
if "prestataire_connecte" not in st.session_state:
    st.session_state.prestataire_connecte = None # (id, nom)

# Gestion fin d'appel
params = st.query_params
if "raccrocher" in params:
    st.session_state.appel_en_cours = None
    st.query_params.clear()
    st.rerun()

est_admin = params.get("admin") == "djassa_admin_secret_2026"

# Barre latérale (Session utilisateur & Espace Prestataire)
with st.sidebar:
    st.header("👤 Votre Session")
    if not st.session_state.utilisateur_pseudo:
        with st.form("form_pseudo"):
            pseudo_saisi = st.text_input("Votre prénom ou pseudo :", placeholder="Ex: Jean Kouassi")
            if st.form_submit_button("Valider mon identité", type="primary"):
                if pseudo_saisi.strip():
                    st.session_state.utilisateur_pseudo = pseudo_saisi.strip()
                    st.rerun()
    else:
        st.info(f"Connecté : **{st.session_state.utilisateur_pseudo}**")
        if st.button("Modifier mon pseudo"):
            st.session_state.utilisateur_pseudo = ""
            st.rerun()
            
    st.markdown("---")
    st.header("🔐 Espace Prestataire")
    if st.session_state.prestataire_connecte is None:
        with st.form("form_login_artisan"):
            nom_art_login = st.text_input("Nom de votre établissement")
            pwd_art_login = st.text_input("Mot de passe", type="password", value="1234")
            if st.form_submit_button("Se connecter au Dashboard"):
                res = verifier_connexion_artisan(nom_art_login.strip(), pwd_art_login.strip())
                if res:
                    st.session_state.prestataire_connecte = res
                    st.success("Connexion réussie !")
                    st.rerun()
                else:
                    st.error("Identifiants incorrects.")
    else:
        st.success(f"Connecté en tant que pro : {st.session_state.prestataire_connecte[1]}")
        if st.button("Se déconnecter du Dashboard"):
            st.session_state.prestataire_connecte = None
            st.rerun()

    st.markdown("---")
    st.subheader(f"⭐ Mes Favoris ({len(st.session_state.favoris)})")
    if st.session_state.favoris:
        for fav in st.session_state.favoris:
            st.markdown(f"- **{fav}**")
    else:
        st.write("Aucun favori enregistré.")

# En-tête principal
st.title("🇨🇮 DJASSA")
st.write("La plateforme de référence pour trouver les meilleurs prestataires et services en Côte d'Ivoire.")

# --- SI UN PRESTATAIRE EST CONNECTÉ : DASHBOARD DÉDIÉ (Étape 6) ---
if st.session_state.prestataire_connecte is not None:
    p_id, p_nom = st.session_state.prestataire_connecte
    st.markdown(f"## 📊 Dashboard de gestion : {p_nom}")
    st.info("Bienvenue dans votre espace pro. Gérez vos clients et consultez vos messages en direct.")
    
    messages_pro = obtenir_messages(p_id)
    avis_pro = obtenir_avis(p_id)
    moy_pro = calculer_moyenne_avis(avis_pro)
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.metric("Total Messages reçus", len(messages_pro))
    with col_d2:
        st.metric("Note Moyenne", f"⭐ {moy_pro} / 5 ({len(avis_pro)} avis)")
        
    st.markdown("---")
    st.subheader("💬 Boîte de réception des clients")
    if messages_pro:
        for msg in messages_pro:
            img_html = f"<br><img src='{msg['image_url']}' style='max-width: 200px; border-radius: 8px;'/>" if msg['image_url'] else ""
            st.markdown(f"""
            <div style="background-color: #1e1e1e; padding: 12px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #444;">
                <strong>De : {msg['expediteur']}</strong> <em>({msg['date_envoi']})</em><br>
                {msg['contenu']}
                {img_html}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("Aucun message client pour le moment.")
        
    st.stop()

# --- VUE PAGE DE CHAT DIRECT (Étape 4) ---
if st.session_state.chat_actif_id is not None:
    artisan_id = st.session_state.chat_actif_id
    artisan_nom = st.session_state.chat_actif_nom
    
    if st.button("← Retour aux recherches", type="secondary"):
        st.session_state.chat_actif_id = None
        st.session_state.chat_actif_nom = ""
        st.rerun()
        
    st.markdown(f"## 💬 Discussion avec {artisan_nom}")
    st.markdown("---")
    
    if not st.session_state.utilisateur_pseudo:
        st.error("⚠️ Veuillez renseigner votre pseudo dans le menu latéral à gauche avant de pouvoir écrire.")
    else:
        messages_artisan = obtenir_messages(artisan_id)
        chat_container = st.container(height=400)
        with chat_container:
            if messages_artisan:
                for msg in reversed(messages_artisan):
                    est_expediteur_actuel = (msg['expediteur'] == st.session_state.utilisateur_pseudo)
                    image_html = f"<br><img src='{msg['image_url']}' style='max-width: 100%; border-radius: 8px; margin-top: 6px;'/>" if msg['image_url'] else ""
                    texte_contenu = f"<br>{msg['contenu']}" if msg['contenu'] else ""
                    
                    bg = "#1e3a8a" if est_expediteur_actuel else "#374151"
                    align = "right" if est_expediteur_actuel else "left"
                    margin = "margin-left: 15%;" if est_expediteur_actuel else "margin-right: 15%;"
                    
                    st.markdown(f"""
                    <div style="background-color: {bg}; padding: 12px 16px; border-radius: 15px; margin: 10px 0; {margin} color: white; text-align: {align};">
                        <span style="font-size: 11px; color: #cbd5e1; display: block; margin-bottom: 3px;">{msg['expediteur']} ({msg['date_envoi']})</span>
                        {texte_contenu}
                        {image_html}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Début de la conversation. Envoyez un message ou une photo !")

        with st.form(f"form_chat_page_{artisan_id}", clear_on_submit=True):
            texte_msg = st.text_input("Votre message...")
            photo_telechargee = st.file_uploader("📷 Joindre une photo", type=["png", "jpg", "jpeg"])
            if st.form_submit_button("Envoyer 🚀", use_container_width=True, type="primary"):
                image_base64 = None
                if photo_telechargee is not None:
                    encoded = base64.b64encode(photo_telechargee.read()).decode()
                    extension = photo_telechargee.name.split('.')[-1]
                    image_base64 = f"data:image/{extension};base64,{encoded}"
                
                if texte_msg.strip() or image_base64:
                    envoyer_message(artisan_id, st.session_state.utilisateur_pseudo, texte_msg.strip(), image_base64)
                    st.rerun()
    st.stop()

# --- NAVIGATION ---
choix_menu = st.radio("Navigation", ["🔍 Rechercher un prestataire", "🗺️ Carte interactive", "📝 Enregistrer un établissement"], horizontal=True)
st.markdown("---")

if choix_menu == "🔍 Rechercher un prestataire":
    
    if st.session_state.appel_en_cours:
        nom_appele = st.session_state.appel_en_cours
        html_appel = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8">
        <style>
            body {{ background-color: #0b0f19; color: white; font-family: sans-serif; display: flex; flex-direction: column; justify-content: space-between; align-items: center; height: 100vh; padding: 40px; }}
            .hangup {{ background-color: #dc2626; width: 65px; height: 65px; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 26px; cursor: pointer; }}
        </style></head>
        <body>
            <h2>{nom_appele}</h2><p>⏳ Appel en cours...</p>
            <div class="hangup" onclick="window.location.href='?raccrocher=1'">📞</div>
        </body></html>
        """
        components.html(html_appel, height=400)
        st.stop()

    st.subheader("Espace de recherche")
    st.info(f"🔥 Déjà **{len(tous_artisans)}** prestataire(s) répertoriés !")
    
    # Recherche par nom
    with st.form("form_recherche_nom"):
        recherche_nom = st.text_input("Recherche directe par nom", placeholder="Ex: Kelo Kelo...")
        if st.form_submit_button("Rechercher par nom", type="primary"):
            if recherche_nom.strip():
                st.session_state.resultats_recherche = rechercher_artisans_intelligent(query=recherche_nom.strip())
                st.rerun()

    st.markdown("---")
    
    # Filtres secteur & commune
    communes_disponibles = ["Toutes les communes"] + sorted(list(set(art['commune'] for art in tous_artisans if art['commune'])))
    with st.form("form_recherche_criteres"):
        metier_cherche = st.text_input("Métier ou secteur (ex: Bar, Boulangerie)")
        commune_selectionnee = st.selectbox("📍 Filtrer par commune", communes_disponibles)
        if st.form_submit_button("Filtrer par critères", type="primary"):
            st.session_state.resultats_recherche = rechercher_artisans_intelligent(query=metier_cherche.strip(), commune_filtre=commune_selectionnee)
            st.rerun()

    # Affichage résultats
    if st.session_state.resultats_recherche is not None:
        resultats = st.session_state.resultats_recherche
        if resultats:
            st.success(f"🎉 {len(resultats)} résultat(s) trouvé(s) !")
            for index_art, artisan in enumerate(resultats):
                artisan_id = artisan['id']
                badge = artisan.get('badge', '⭐ Professionnel')
                
                with st.container():
                    st.markdown(f"""
                    <div style="padding: 15px; border-radius: 10px; border: 1px solid #333; margin-bottom: 10px; background-color: #1e1e1e;">
                        <h3 style="margin:0; color:#3b82f6; font-size:18px;">{artisan['nom']}</h3>
                        <p style="margin:5px 0; color:#e5e7eb;"><strong>{artisan['metier']}</strong> - 📍 {artisan['commune']}</p>
                        <p style="margin:0; color:#9ca3af; font-size:13px;">{artisan['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f'<a href="{artisan["appel_url"]}" target="_self"><button style="background-color:#2563eb; color:white; padding:8px; border:none; border-radius:6px; width:100%; font-weight:bold;">📞 Appeler</button></a>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<a href="{artisan["whatsapp_url"]}" target="_blank"><button style="background-color:#22c55e; color:white; padding:8px; border:none; border-radius:6px; width:100%; font-weight:bold;">🟢 WhatsApp</button></a>', unsafe_allow_html=True)
                
                if st.button(f"💬 Chat en direct avec {artisan['nom']}", key=f"chat_{artisan_id}", use_container_width=True, type="primary"):
                    st.session_state.chat_actif_id = artisan_id
                    st.session_state.chat_actif_nom = artisan['nom']
                    st.rerun()
                    
                # Gestion des favoris (Étape 8)
                is_fav = artisan['nom'] in st.session_state.favoris
                if not is_fav:
                    if st.button(f"⭐ Ajouter aux favoris", key=f"fav_{artisan_id}", use_container_width=True):
                        st.session_state.favoris.append(artisan['nom'])
                        st.rerun()
                else:
                    if st.button(f"❌ Retirer des favoris", key=f"unfav_{artisan_id}", use_container_width=True):
                        st.session_state.favoris.remove(artisan['nom'])
                        st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.warning("Aucun établissement trouvé.")

# --- CARTE INTERACTIVE (Étape 7) ---
elif choix_menu == "🗺️ Carte interactive":
    st.subheader("🗺️ Localisation des prestataires à Abidjan")
    st.write("Visualisez l'emplacement géographique des services répertoriés sur la plateforme.")
    
    if tous_artisans:
        # Création d'un DataFrame pour la carte native Streamlit
        df_map = pd.DataFrame(tous_artisans)
        # On renomme pour que streamlit comprenne latitude/longitude
        df_map = df_map.rename(columns={"lat": "latitude", "lon": "longitude"})
        st.map(df_map, latitude="latitude", longitude="longitude", size=50, color="#f97316")
    else:
        st.info("Aucun prestataire à afficher sur la carte pour l'instant.")

# --- ENREGISTREMENT ---
elif choix_menu == "📝 Enregistrer un établissement":
    st.subheader("Enregistrer un nouvel établissement")
    with st.form("form_enregistrement"):
        nom = st.text_input("Nom de l'établissement")
        metier = st.text_input("Métier ou secteur")
        commune = st.text_input("Commune (ex: Cocody, Marcory)")
        description = st.text_area("Courte description")
        password = st.text_input("Mot de passe Espace Pro (par défaut 1234)", value="1234")
        telephone = st.text_input("Numéro de téléphone (+225...)")
        
        if st.form_submit_button("Enregistrer", type="primary"):
            if nom and metier and commune and telephone:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO artisans (nom, metier, commune, description, badge, appel_url, whatsapp_url, password)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (nom.strip(), metier.strip().capitalize(), commune.strip().capitalize(), description.strip(), "⭐ Professionnel", f"tel:{telephone}", f"https://wa.me/{telephone.replace('+', '').replace(' ', '')}", password.strip()))
                conn.commit()
                conn.close()
                st.success("Enregistré avec succès !")
                st.rerun()
            else:
                st.error("Remplissez les champs obligatoires.")
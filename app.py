import streamlit as st
import pandas as pd
import base64
import database

# Initialisation sécurisée de la base de données
try:
    database.init_db()
except Exception as e:
    st.error(f"Erreur de démarrage de la base de données : {e}")

st.set_page_config(page_title="DJASSA", page_icon="🇨🇮", layout="centered")

# --- DESIGN IDENTIQUE À TRANSFERT CI (BANDEAU ORANGE & COMPOSANTS) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background-color: #F7F8FA;
    }
    
    /* Grand bandeau supérieur orange arrondi */
    .hero-banner {
        background: linear-gradient(135deg, #FF7A00 0%, #FF9900 100%);
        padding: 30px 20px 70px 20px;
        border-radius: 0 0 35px 35px;
        color: white;
        text-align: center;
        box-shadow: 0px 8px 20px rgba(255, 122, 0, 0.25);
    }
    .hero-banner h1 {
        margin: 0;
        font-size: 34px;
        font-weight: 900;
    }
    .hero-banner p {
        margin: 5px 0 0 0;
        font-size: 15px;
        opacity: 0.95;
    }

    /* Carte Scanner centrale en relief */
    .scanner-card {
        background: white;
        padding: 25px;
        border-radius: 24px;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.08);
        text-align: center;
        margin: -50px auto 25px auto;
        width: 85%;
        max-width: 400px;
        border: 1px solid #F0F0F0;
    }

    /* Boutons de navigation et actions */
    .stButton>button {
        background-color: #FF7A00;
        color: white !important;
        border-radius: 14px;
        border: none;
        font-weight: bold;
        padding: 12px 24px;
        width: 100%;
        box-shadow: 0px 4px 12px rgba(255, 122, 0, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #E06B00;
        transform: translateY(-2px);
    }
    </style>
""", unsafe_allow_html=True)

# 1. Bandeau supérieur orange
st.markdown("""
    <div class="hero-banner">
        <h1>🇨🇮 DJASSA</h1>
        <p>Votre plateforme de services et proximité en Côte d'Ivoire</p>
    </div>
""", unsafe_allow_html=True)

# 2. Carte centrale style "Scanner / Action rapide"
st.markdown("""
    <div class="scanner-card">
        <h3 style="margin:0 0 10px 0; color:#2C3E50; font-size:18px;">📱 Accès Rapide & Flash</h3>
        <p style="color:#7F8C8D; font-size:13px; margin:0;">Scannez ou choisissez un service ci-dessous</p>
    </div>
""", unsafe_allow_html=True)

# 3. Menu de sélection des fonctions propres à DJASSA (avec logos/icônes adaptés)
menu_choix = st.selectbox(
    "🧭 Sélectionnez une fonctionnalité :", 
    [
        "🔍 Annuaire & Artisans", 
        "🏥 Pharmacies de Garde", 
        "🌐 Pass Internet & Offres Mobiles", 
        "🛠️ Espace Prestataire", 
        "👑 Espace Administrateur"
    ]
)

st.markdown("---")

communes_liste = ["Toutes les communes", "Cocody", "Yopougon", "Plateau", "Marcory", "Adjamé", "Treichville", "Riviera", "Koumassi", "Port-Bouët", "Abobo", "Bingerville"]

if menu_choix == "🔍 Annuaire & Artisans":
    st.header("🔍 Rechercher un artisan ou un service")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        recherche_nom = st.text_input("Nom ou entreprise")
    with col2:
        commune_filtre = st.selectbox("Commune", communes_liste)
    with col3:
        metiers_dispo = ["Tous les services", "Plombier", "Menuisier", "Électricien", "Maçon", "Peintre", "Climatisation", "Mécanicien", "Couturier"]
        metier_filtre = st.selectbox("Métier", metiers_dispo)
    
    query_finale = recherche_nom
    if metier_filtre != "Tous les services":
        query_finale = f"{recherche_nom} {metier_filtre}".strip()

    artisans = database.rechercher_artisans_intelligent(query=query_finale, commune_filtre=commune_filtre)
    
    if not artisans:
        st.info("Aucun artisan trouvé avec ces critères.")
    else:
        st.success(f"{len(artisans)} prestataire(s) trouvé(s)")
        
        st.subheader("🗺️ Carte des prestataires")
        df_map = pd.DataFrame([{"lat": a["lat"], "lon": a["lon"]} for a in artisans if a.get("lat") and a.get("lon")])
        if not df_map.empty:
            st.map(df_map, zoom=11)
        st.markdown("---")

        for art in artisans:
            moyenne, nb_avis = database.obtenir_note_moyenne(art['id'])
            etoiles_affichage = f"⭐ {moyenne}/5 ({nb_avis} avis)" if nb_avis > 0 else "⭐ Nouveau"

            with st.expander(f"🛠️ {art['nom']} - {art['metier']} ({art['commune']}) | {etoiles_affichage}"):
                st.write(f"**Description :** {art['description']}")
                st.write(f"**Badge :** {art['badge']}")
                
                c_appel, c_wa = st.columns(2)
                with c_appel:
                    if art['appel_url']:
                        st.link_button("📞 Appeler", art['appel_url'])
                with c_wa:
                    if art['whatsapp_url']:
                        st.link_button("💬 WhatsApp", art['whatsapp_url'])
                
                st.markdown("---")
                
                portfolio_images = database.obtenir_portfolio(art['id'])
                if portfolio_images:
                    st.subheader("📸 Portfolio & Réalisations")
                    cols = st.columns(3)
                    for i, img_data in enumerate(portfolio_images):
                        with cols[i % 3]:
                            st.image(f"data:image/png;base64,{img_data['image_b64']}", caption=img_data['description'], use_container_width=True)
                    st.markdown("---")

                st.subheader("💬 Discuter en direct")
                messages = database.obtenir_messages(art['id'])
                
                chat_container = st.container(height=200)
                with chat_container:
                    if messages:
                        for msg in messages:
                            st.write(f"**{msg['expediteur']}** : {msg['contenu']}")
                    else:
                        st.caption("Aucun message pour l'instant.")
                
                with st.form(f"form_chat_{art['id']}", clear_on_submit=True):
                    nom_expediteur = st.text_input("Votre nom / pseudo", key=f"exp_{art['id']}")
                    texte_message = st.text_input("Votre message", key=f"txt_{art['id']}")
                    if st.form_submit_button("Envoyer le message"):
                        if nom_expediteur and texte_message:
                            database.envoyer_message(art['id'], nom_expediteur, texte_message)
                            st.success("Message envoyé !")
                            st.rerun()
                        else:
                            st.warning("Remplissez votre nom et votre message.")

                st.markdown("---")
                st.subheader(f"⭐ Avis clients ({moyenne}/5 sur {nb_avis} avis)")
                avis_list = database.obtenir_avis(art['id'])
                if avis_list:
                    for av in avis_list:
                        st.write(f"⭐ **{av['note']}/5** : {av['commentaire']}")
                else:
                    st.write("Pas encore d'avis.")
                    
                with st.form(f"form_avis_{art['id']}"):
                    note = st.slider("Note", 1, 5, 5, key=f"slider_{art['id']}")
                    commentaire = st.text_area("Votre commentaire", key=f"comm_{art['id']}")
                    if st.form_submit_button("Laisser un avis"):
                        database.ajouter_avis(art['id'], note, commentaire)
                        st.success("Avis ajouté !")
                        st.rerun()

elif menu_choix == "🏥 Pharmacies de Garde":
    st.header("🏥 Pharmacies de Garde")
    st.write("Trouvez rapidement les pharmacies ouvertes pour les urgences cette semaine.")
    
    commune_pharma = st.selectbox("Sélectionnez votre commune :", communes_liste)
    pharmacies_trouvees = database.obtenir_pharmacies(commune_filtre=commune_pharma)
    
    if pharmacies_trouvees:
        for ph in pharmacies_trouvees:
            with st.container():
                st.subheader(f"💊 {ph['nom']}")
                st.write(f"📍 **Commune :** {ph['commune']}")
                st.write(f"🗺️ **Localisation :** {ph['localisation']}")
                if ph['contact']:
                    st.link_button("📞 Appeler la pharmacie", f"tel:{ph['contact']}")
                st.divider()
    else:
        st.info("Aucune pharmacie de garde enregistrée pour cette commune actuellement.")

elif menu_choix == "🌐 Pass Internet & Offres Mobiles":
    st.header("🌐 Souscription de Forfaits Mobiles")
    st.write("Le même procédé instantané : choisissez votre réseau, sélectionnez votre pass, entrez votre numéro et procédez au paiement.")
    
    operateur = st.selectbox("1. Choisissez l'opérateur :", ["Orange Côte d'Ivoire", "MTN Côte d'Ivoire", "Moov Africa CI"])
    
    offres_par_operateur = {
        "Orange Côte d'Ivoire": {
            "🔥 [Offre Perso] Pass Bonus Yamo (200F - 220 Mo)": 200,
            "⚡ Pass Nuit (250F - 2 Go)": 250,
            "📅 Pass 24H (500F - 750 Mo)": 500,
            "📆 Pass Semaine (1 000F - 1.5 Go)": 1000,
            "🌙 Pass Mois (5 000F - 7.2 Go)": 5000,
            "🌙 Pass Mois (10 000F - 15 Go)": 10000
        },
        "MTN Côte d'Ivoire": {
            "🔥 [Offre Perso] Pass Awoulaba (150F - 150 Mo)": 150,
            "⚡ Pass Nuit Max (300F - 3 Go)": 300,
            "📅 Pass Jour (300F - 400 Mo)": 300,
            "📆 Pass Semaine (1 000F - 1.5 Go)": 1000,
            "🌙 Pass Mois (2 500F - 5 Go)": 2500,
            "🌙 Pass Mois (10 000F - 25 Go)": 10000
        },
        "Moov Africa CI": {
            "🔥 [Offre Perso] Pass Flooz Bonus (150F - 150 Mo)": 150,
            "⚡ Pass Nuit (200F - 2 Go)": 200,
            "📅 Pass Weekend (500F - 2.5 Go)": 500,
            "📆 Pass Semaine (750F - 1 Go)": 750,
            "🌙 Pass Mois (5 000F - 7 Go)": 5000,
            "🌙 Pass Mois (10 000F - 20 Go)": 10000
        }
    }
    
    st.markdown("---")
    st.subheader("2. Sélectionnez votre offre")
    pass_choisi = st.selectbox("Catalogue des offres :", list(offres_par_operateur[operateur].keys()))
    montant = offres_par_operateur[operateur][pass_choisi]
    
    st.markdown(f"💳 **Montant à régler :** `{montant} FCFA`")
    
    st.markdown("---")
    st.subheader("3. Numéro de téléphone & Paiement Wave")
    
    with st.form("form_souscription"):
        numero_client = st.text_input("Votre numéro de téléphone (ex: 07 / 05 / 01...)")
        
        if st.form_submit_button("🚀 Valider et Payer avec Wave"):
            if numero_client and len(numero_client) >= 10:
                st.success(f"✅ Commande enregistrée pour le **{numero_client}** !")
                st.info(f"Montant : **{montant} FCFA** - Redirection vers la passerelle **Wave**...")
                st.link_button("👉 Ouvrir l'application Wave pour régler", "https://pay.wave.com/")
            else:
                st.error("Veuillez entrer un numéro de téléphone valide à 10 chiffres.")

elif menu_choix == "🛠️ Espace Prestataire":
    st.header("🛠️ Espace Prestataire")
    
    if 'artisan_id' in st.session_state:
        st.success(f"🟢 Connecté en tant que : **{st.session_state['artisan_nom']}**")
        
        if st.button("🚪 Se déconnecter"):
            del st.session_state['artisan_id']
            del st.session_state['artisan_nom']
            st.rerun()
            
        st.markdown("---")
        st.subheader("📸 Ajouter une réalisation au Portfolio")
        uploaded_file = st.file_uploader("Choisissez une image de votre travail", type=["png", "jpg", "jpeg"])
        desc_image = st.text_input("Petite description de l'image")
        
        if st.button("Ajouter l'image"):
            if uploaded_file is not None:
                bytes_data = uploaded_file.getvalue()
                image_b64 = base64.b64encode(bytes_data).decode()
                database.ajouter_image_portfolio(st.session_state['artisan_id'], image_b64, desc_image)
                st.success("Image ajoutée à votre profil !")
                st.rerun()
            else:
                st.warning("Sélectionnez une image.")
        
        st.markdown("---")
        st.subheader("📬 Vos Messages Reçus")
        messages_recus = database.obtenir_messages(st.session_state['artisan_id'])
        if messages_recus:
            for msg in reversed(messages_recus):
                date_str = msg['date_envoi'].strftime('%d/%m/%Y à %H:%M')
                st.info(f"**De {msg['expediteur']}** ({date_str}) :\n\n{msg['contenu']}")
        else:
            st.write("Aucun message reçu.")
            
        st.markdown("---")
        st.subheader("⭐ Vos Avis Clients")
        avis_recus = database.obtenir_avis(st.session_state['artisan_id'])
        if avis_recus:
            for av in avis_recus:
                st.write(f"⭐ **{av['note']}/5** : {av['commentaire']}")
        else:
            st.write("Aucun avis reçu.")
            
    else:
        action = st.radio("Que souhaitez-vous faire ?", ["S'inscrire", "Se connecter"])
        
        if action == "S'inscrire":
            st.subheader("Enregistrer votre établissement")
            with st.form("form_inscription"):
                nom = st.text_input("Nom de l'entreprise ou de l'artisan")
                metier = st.text_input("Métier / Service (ex: Plombier...)")
                commune = st.selectbox("Commune", communes_liste[1:])
                description = st.text_area("Description")
                badge = st.text_input("Badge (ex: Vérifié)")
                appel_url = st.text_input("Lien d'appel (tel:+225...)")
                whatsapp_url = st.text_input("Lien WhatsApp (https://wa.me/...)")
                password = st.text_input("Mot de passe", type="password")
                
                if st.form_submit_button("Valider l'enregistrement"):
                    if nom and metier and password:
                        database.ajouter_artisan(nom, metier, commune, description, badge, appel_url, whatsapp_url, password)
                        st.success("Établissement enregistré avec succès !")
                    else:
                        st.error("Remplissez au moins le nom, le métier et le mot de passe.")

        elif action == "Se connecter":
            st.subheader("Connexion Prestataire")
            nom_connexion = st.text_input("Votre nom d'artisan / entreprise")
            pwd_connexion = st.text_input("Votre mot de passe", type="password")
            
            if st.button("Se connecter"):
                artisan_verif = database.verifier_connexion_artisan(nom_connexion, pwd_connexion)
                if artisan_verif:
                    st.session_state['artisan_id'] = artisan_verif[0]
                    st.session_state['artisan_nom'] = artisan_verif[1]
                    st.rerun()
                else:
                    st.error("Nom ou mot de passe incorrect.")

elif menu_choix == "👑 Espace Administrateur":
    st.header("👑 Panneau de Contrôle Administrateur")
    
    admin_pwd = st.text_input("Mot de passe administrateur", type="password")
    
    if admin_pwd == "djassa_admin_2026":
        st.success("Accès autorisé. Bienvenue boss !")
        
        st.subheader("📊 Statistiques de la plateforme")
        nb_artisans, nb_avis, nb_messages = database.obtenir_toutes_les_stats()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Prestataires inscrits", nb_artisans)
        col2.metric("Avis publiés", nb_avis)
        col3.metric("Messages envoyés", nb_messages)
        
        st.markdown("---")
        st.subheader("🏥 Gérer les Pharmacies de Garde")
        with st.form("form_ajout_pharma"):
            p_nom = st.text_input("Nom de la pharmacie")
            p_commune = st.selectbox("Commune", communes_liste[1:])
            p_contact = st.text_input("Contact (+225...)")
            p_loc = st.text_input("Localisation précise")
            
            if st.form_submit_button("Ajouter cette pharmacie"):
                database.ajouter_pharmacie(p_nom, p_commune, p_contact, p_loc)
                st.success(f"Pharmacie {p_nom} ajoutée !")
                st.rerun()
                
        if st.button("🗑️ Vider la liste des pharmacies"):
            database.vider_pharmacies()
            st.success("Liste vidée.")
            st.rerun()
        
        st.markdown("---")
        st.subheader("🛠️ Gérer les prestataires")
        tous_les_artisans = database.obtenir_tous_les_artisans_admin()
        
        if tous_les_artisans:
            for art in tous_les_artisans:
                with st.container():
                    col_nom, col_btn = st.columns([3, 1])
                    with col_nom:
                        st.write(f"**{art['nom']}** - {art['metier']} ({art['commune']})")
                    with col_btn:
                        if st.button("❌ Supprimer", key=f"del_{art['id']}"):
                            database.supprimer_artisan(art['id'])
                            st.rerun()
                st.divider()
        else:
            st.info("Aucun prestataire inscrit.")
            
    elif admin_pwd != "":
        st.error("Mot de passe incorrect.")
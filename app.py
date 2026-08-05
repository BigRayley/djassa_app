import streamlit as st
import pandas as pd
import base64
import database

database.init_db()

# Configuration de la page
st.set_page_config(page_title="DJASSA", page_icon="🇨🇮", layout="centered")

# --- INJECTION DE CSS POUR LE DESIGN (UI) ---
st.markdown("""
    <style>
    /* Cacher le menu par défaut de Streamlit et le footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Design des boutons principaux */
    .stButton>button {
        background-color: #FF8C00; /* Orange dynamique */
        color: white !important;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #E67E22;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        transform: scale(1.02);
    }

    /* Design des onglets et expanders (cartes artisans) */
    .streamlit-expanderHeader {
        background-color: #F8F9FA;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        font-weight: bold;
        font-size: 16px;
    }
    
    /* Titre principal personnalisé */
    .titre-djassa {
        text-align: center;
        color: #2C3E50;
        font-size: 40px;
        font-weight: 900;
        margin-bottom: 5px;
    }
    .sous-titre {
        text-align: center;
        color: #7F8C8D;
        font-size: 18px;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# Affichage du titre avec notre nouveau style
st.markdown('<div class="titre-djassa">🇨🇮 DJASSA</div>', unsafe_allow_html=True)
st.markdown('<div class="sous-titre">Connectez-vous aux artisans et prestataires en Côte d\'Ivoire</div>', unsafe_allow_html=True)

menu = ["Accueil / Recherche", "Espace Prestataire (Inscription / Connexion)", "Espace Administrateur"]
choix = st.sidebar.selectbox("Navigation", menu)

if choix == "Accueil / Recherche":
    st.header("🔍 Rechercher un service ou un artisan")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        recherche_nom = st.text_input("Nom de l'artisan / entreprise")
    with col2:
        communes_dispo = ["Toutes les communes", "Cocody", "Yopougon", "Plateau", "Marcory", "Adjamé", "Treichville", "Riviera", "Koumassi", "Port-Bouët", "Abobo", "Bingerville"]
        commune_filtre = st.selectbox("Commune", communes_dispo)
    with col3:
        metiers_dispo = ["Tous les services", "Plombier", "Menuisier", "Électricien", "Maçon", "Peintre", "Climatisation", "Mécanicien", "Couturier"]
        metier_filtre = st.selectbox("Service / Métier", metiers_dispo)
    
    query_finale = recherche_nom
    if metier_filtre != "Tous les services":
        query_finale = f"{recherche_nom} {metier_filtre}".strip()

    artisans = database.rechercher_artisans_intelligent(query=query_finale, commune_filtre=commune_filtre)
    
    if not artisans:
        st.info("Aucun artisan trouvé avec ces critères.")
    else:
        st.success(f"{len(artisans)} artisan(s) trouvé(s)")
        
        st.subheader("🗺️ Carte des artisans")
        df_map = pd.DataFrame([{"lat": a["lat"], "lon": a["lon"]} for a in artisans if a.get("lat") and a.get("lon")])
        if not df_map.empty:
            st.map(df_map, zoom=11)
        st.markdown("---")

        for art in artisans:
            moyenne, nb_avis = database.obtenir_note_moyenne(art['id'])
            etoiles_affichage = f"⭐ {moyenne}/5 ({nb_avis} avis)" if nb_avis > 0 else "⭐ Nouveau"

            with st.expander(f"{art['nom']} - {art['metier']} ({art['commune']}) | {etoiles_affichage}"):
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

                st.subheader("💬 Discuter en direct avec l'artisan")
                messages = database.obtenir_messages(art['id'])
                
                chat_container = st.container(height=200)
                with chat_container:
                    if messages:
                        for msg in messages:
                            st.write(f"**{msg['expediteur']}** : {msg['contenu']}")
                    else:
                        st.caption("Aucun message pour l'instant. Envoyez le premier !")
                
                with st.form(f"form_chat_{art['id']}", clear_on_submit=True):
                    nom_expediteur = st.text_input("Votre nom / pseudo", key=f"exp_{art['id']}")
                    texte_message = st.text_input("Votre message", key=f"txt_{art['id']}")
                    send_msg = st.form_submit_button("Envoyer le message")
                    if send_msg:
                        if nom_expediteur and texte_message:
                            database.envoyer_message(art['id'], nom_expediteur, texte_message)
                            st.success("Message envoyé !")
                            st.rerun()
                        else:
                            st.warning("Veuillez remplir votre nom et votre message.")

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
                    submit_avis = st.form_submit_button("Laisser un avis")
                    if submit_avis:
                        database.ajouter_avis(art['id'], note, commentaire)
                        st.success("Avis ajouté avec succès !")
                        st.rerun()

elif choix == "Espace Prestataire (Inscription / Connexion)":
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
        desc_image = st.text_input("Petite description de l'image (ex: Meuble sur mesure)")
        
        if st.button("Ajouter l'image"):
            if uploaded_file is not None:
                bytes_data = uploaded_file.getvalue()
                image_b64 = base64.b64encode(bytes_data).decode()
                database.ajouter_image_portfolio(st.session_state['artisan_id'], image_b64, desc_image)
                st.success("Super ! L'image a été ajoutée à votre profil.")
                st.rerun()
            else:
                st.warning("Veuillez sélectionner une image avant de valider.")
        
        st.markdown("---")
        
        st.subheader("📬 Vos Messages Reçus")
        messages_recus = database.obtenir_messages(st.session_state['artisan_id'])
        if messages_recus:
            for msg in reversed(messages_recus):
                date_str = msg['date_envoi'].strftime('%d/%m/%Y à %H:%M')
                st.info(f"**De {msg['expediteur']}** ({date_str}) :\n\n{msg['contenu']}")
        else:
            st.write("Aucun message reçu pour le moment.")
            
        st.markdown("---")
        st.subheader("⭐ Vos Avis Clients")
        avis_recus = database.obtenir_avis(st.session_state['artisan_id'])
        if avis_recus:
            for av in avis_recus:
                st.write(f"⭐ **{av['note']}/5** : {av['commentaire']}")
        else:
            st.write("Aucun avis reçu pour le moment.")
            
    else:
        action = st.radio("Que souhaitez-vous faire ?", ["S'inscrire", "Se connecter"])
        
        if action == "S'inscrire":
            st.subheader("Enregistrer un nouvel établissement / service")
            with st.form("form_inscription"):
                nom = st.text_input("Nom de l'entreprise ou de l'artisan")
                metier = st.text_input("Métier / Service (ex: Plombier, Menuisier...)")
                commune = st.selectbox("Commune", ["Cocody", "Yopougon", "Plateau", "Marcory", "Adjamé", "Treichville", "Riviera", "Koumassi", "Port-Bouët", "Abobo", "Bingerville"])
                description = st.text_area("Description de vos services")
                badge = st.text_input("Badge (ex: Vérifié, Professionnel...)")
                appel_url = st.text_input("Lien d'appel (ex: tel:+225...)")
                whatsapp_url = st.text_input("Lien WhatsApp (ex: https://wa.me/225...)")
                password = st.text_input("Mot de passe pour gérer votre espace", type="password")
                
                submit_artisan = st.form_submit_button("Valider l'enregistrement")
                
                if submit_artisan:
                    if nom and metier and password:
                        database.ajouter_artisan(
                            nom=nom,
                            metier=metier,
                            commune=commune,
                            description=description,
                            badge=badge,
                            appel_url=appel_url,
                            whatsapp_url=whatsapp_url,
                            password=password
                        )
                        st.success("Établissement enregistré avec succès dans le cloud !")
                    else:
                        st.error("Veuillez remplir au moins le nom, le métier et le mot de passe.")

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

elif choix == "Espace Administrateur":
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
            st.info("Aucun prestataire inscrit pour le moment.")
            
    elif admin_pwd != "":
        st.error("Mot de passe incorrect.")
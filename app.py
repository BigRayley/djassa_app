import streamlit as st
import database

database.init_db()

st.set_page_config(page_title="DJASSA", page_icon="🇨🇮", layout="centered")

st.title("🇨🇮 DJASSA")
st.subheader("Connectez-vous aux artisans et prestataires en Côte d'Ivoire")

menu = ["Accueil / Recherche", "Espace Prestataire (Inscription / Connexion)"]
choix = st.sidebar.selectbox("Navigation", menu)

if choix == "Accueil / Recherche":
    st.header("🔍 Rechercher un service ou un artisan")
    
    # Séparation en 3 barres de recherche distinctes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        recherche_nom = st.text_input("Nom de l'artisan / entreprise")
    with col2:
        # Liste des communes de Côte d'Ivoire / Abidjan
        communes_dispo = ["Toutes les communes", "Cocody", "Yopougon", "Plateau", "Marcory", "Adjamé", "Treichville", "Riviera", "Koumassi", "Port-Bouët", "Abobo", "Bingerville"]
        commune_filtre = st.selectbox("Commune", communes_dispo)
    with col3:
        # Métiers / Services
        metiers_dispo = ["Tous les services", "Plombier", "Menuisier", "Électricien", "Maçon", "Peintre", "Climatisation", "Mécanicien", "Couturier"]
        metier_filtre = st.selectbox("Service / Métier", metiers_dispo)
    
    # Recherche intelligente combinant les critères
    query_finale = recherche_nom
    if metier_filtre != "Tous les services":
        query_finale = f"{recherche_nom} {metier_filtre}".strip()

    artisans = database.rechercher_artisans_intelligent(query=query_finale, commune_filtre=commune_filtre)
    
    if not artisans:
        st.info("Aucun artisan trouvé avec ces critères.")
    else:
        st.success(f"{len(artisans)} artisan(s) trouvé(s)")
        for art in artisans:
            with st.expander(f"{art['nom']} - {art['metier']} ({art['commune']})"):
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
                st.subheader("Avis clients")
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
                st.success(f"Bienvenue, {artisan_verif[1]} !")
                st.session_state['artisan_id'] = artisan_verif[0]
                st.session_state['artisan_nom'] = artisan_verif[1]
            else:
                st.error("Nom ou mot de passe incorrect.")
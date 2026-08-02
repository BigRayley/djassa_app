import json
import streamlit as st

st.set_page_config(page_title="DJASSA - Bêta", page_icon="🇨🇮", layout="centered")

st.title("🇨🇮 DJASSA")
st.write("La plateforme de référence pour trouver les meilleurs prestataires et services en Côte d'Ivoire.")

# Chargement des prestataires depuis le fichier JSON
try:
    with open("data.json", "r", encoding="utf-8") as f:
        artisans = json.load(f)
except FileNotFoundError:
    artisans = []

# Menu de navigation
menu = st.sidebar.selectbox("Navigation", ["🔍 Rechercher un prestataire", "📝 Enregistrer un établissement"])

if menu == "🔍 Rechercher un prestataire":
    st.subheader("Espace de recherche")
    
    # Compteur dynamique
    st.info(f"🔥 Déjà **{len(artisans)}** prestataire(s) et établissement(s) répertoriés sur la plateforme !")
    
    # Recherche textuelle classique
    metier_cherche = st.text_input("Métier ou secteur recherché (ex: Plombier, Hôtel Résidence, Maquis)")
    
    # Filtres rapides par commune en un clic (Étape 2)
    st.write("**Ou filtrez rapidement par commune :**")
    cols_communes = st.columns(4)
    commune_selectionnee = ""
    
    communes_populaires = ["Cocody", "Yopougon", "Marcory", "Plateau"]
    for i, com in enumerate(communes_populaires):
        with cols_communes[i]:
            if st.button(com, use_container_width=True):
                commune_selectionnee = com

    # Champ texte pour la commune (pré-rempli si un bouton rapide est cliqué)
    commune_cherche = st.text_input("Commune (ex: Cocody, Yopougon)", value=commune_selectionnee)

    if st.button("Lancer la recherche", type="primary"):
        resultats = []
        for artisan in artisans:
            metier_match = metier_cherche.lower() in artisan['metier'].lower() if metier_cherche else True
            commune_match = commune_cherche.lower() in artisan['commune'].lower() if commune_cherche else True
            
            if metier_match and commune_match:
                resultats.append(artisan)

        if resultats:
            st.success(f"{len(resultats)} prestataire(s) trouvé(s) !")
            for artisan in resultats:
                st.markdown("---")
                st.subheader(f"{artisan['nom']}")
                st.write(f"**Métier / Secteur:** {artisan['metier']}")
                st.write(f"**Commune:** {artisan['commune']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f'<a href="{artisan["appel_url"]}" target="_self"><button style="background-color:#4CAF50; color:white; padding:8px 16px; border:none; border-radius:4px; cursor:pointer; width:100%;">📞 Appeler</button></a>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<a href="{artisan["whatsapp_url"]}" target="_blank"><button style="background-color:#25D366; color:white; padding:8px 16px; border:none; border-radius:4px; cursor:pointer; width:100%;">💬 WhatsApp</button></a>', unsafe_allow_html=True)
        else:
            st.warning("Aucun prestataire trouvé pour ces critères.")

elif menu == "📝 Enregistrer un établissement":
    st.subheader("Enregistrer un nouveau prestataire ou établissement")
    
    with st.form("form_enregistrement"):
        nom = st.text_input("Nom de l'établissement ou de l'artisan")
        metier = st.text_input("Métier ou secteur (ex: Plombier, Hôtel Résidence, Maquis Bar)")
        commune = st.text_input("Commune (ex: Cocody, Yopougon, Marcory)")
        telephone = st.text_input("Numéro de téléphone (ex: +2250102030405)")
        
        submit_button = st.form_submit_button("Enregistrer l'établissement", type="primary")
        
        if submit_button:
            if nom and metier and commune and telephone:
                nouveau_prestataire = {
                    "nom": nom,
                    "metier": metier,
                    "commune": commune,
                    "appel_url": f"tel:{telephone}",
                    "whatsapp_url": f"https://wa.me/{telephone.replace('+', '')}"
                }
                
                artisans.append(nouveau_prestataire)
                with open("data.json", "w", encoding="utf-8") as f:
                    json.dump(artisans, f, ensure_ascii=False, indent=2)
                
                st.success("🎉 Établissement enregistré avec succès ! Il est désormais visible dans la recherche.")
            else:
                st.error("Veuillez remplir tous les champs du formulaire.")
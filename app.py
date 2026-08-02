import json
import urllib.parse
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

# --- SECURITE ADMIN CACHEE PAR URL ---
# On vérifie si l'URL contient ton paramètre secret (ex: tonapp.streamlit.app/?admin=moncode2026)
params = st.query_params
est_admin = params.get("admin") == "djassa_admin_secret_2026"

# Liste des menus dynamiques (l'admin n'apparaît que pour toi via l'URL secrète)
options_menu = ["🔍 Rechercher un prestataire", "📝 Enregistrer un établissement"]
if est_admin:
    options_menu.append("⚙️ Administration")

# Menu de navigation
menu = st.sidebar.selectbox("Navigation", options_menu)

if menu == "🔍 Rechercher un prestataire":
    st.subheader("Espace de recherche")
    
    # Compteur dynamique
    st.info(f"🔥 Déjà **{len(artisans)}** prestataire(s) et établissement(s) répertoriés sur la plateforme !")
    
    # Recherche textuelle classique
    metier_cherche = st.text_input("Métier ou secteur recherché (ex: Plombier, Hôtel Résidence, Maquis)")
    
    # Filtres rapides par commune en un clic
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
                with st.container():
                    st.markdown(
                        f"""
                        <div style="padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0; margin-bottom: 15px; background-color: #1e1e1e;">
                            <h3 style="margin: 0; color: #ffffff;">{artisan['nom']}</h3>
                            <p style="margin: 5px 0; color: #b0b0b0;"><strong>Métier:</strong> {artisan['metier']} | <strong>Commune:</strong> {artisan['commune']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f'<a href="{artisan["appel_url"]}" target="_self"><button style="background-color:#4CAF50; color:white; padding:10px 16px; border:none; border-radius:6px; cursor:pointer; width:100%; font-weight:bold;">📞 Appeler</button></a>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<a href="{artisan["whatsapp_url"]}" target="_blank"><button style="background-color:#25D366; color:white; padding:10px 16px; border:none; border-radius:6px; cursor:pointer; width:100%; font-weight:bold;">💬 WhatsApp</button></a>', unsafe_allow_html=True)
                
                # Bouton de partage individuel du prestataire sur WhatsApp
                texte_partage = urllib.parse.quote(f"Salut ! Je te partage ce contact trouvé sur DJASSA 🇨🇮 :\n*{artisan['nom']}* ({artisan['metier']}) à {artisan['commune']}.")
                st.markdown(f'<a href="https://wa.me/?text={texte_partage}" target="_blank"><button style="background-color:#128C7E; color:white; padding:8px 12px; border:none; border-radius:6px; cursor:pointer; width:100%; font-size:13px; margin-top:5px;">📤 Recommander ce prestataire sur WhatsApp</button></a>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.warning("Aucun prestataire trouvé pour ces critères.")
            
    # Section À la une / Récemment ajoutés
    st.markdown("---")
    st.subheader("🌟 Récemment ajoutés sur la plateforme")
    if artisans:
        derniers = artisans[-3:]
        for art in reversed(derniers):
            st.markdown(f"- **{art['nom']}** ({art['metier']}) à *{art['commune']}*")
    else:
        st.write("Aucun établissement pour le moment.")

elif menu == "📝 Enregistrer un établissement":
    st.subheader("Enregistrer un nouveau prestataire ou établissement")
    
    with st.form("form_enregistrement"):
        nom = st.text_input("Nom de l'établissement ou de l'artisan")
        metier = st.text_input("Métier ou secteur (ex: Plombier, Hôtel Résidence, Maquis Bar)")
        commune = st.text_input("Commune (ex: Cocody, Yopougon, Marcory)")
        telephone = st.text_input("Numéro de téléphone (ex: +2250102030405)")
        
        submit_button = st.form_submit_button("Enregistrer l'établissement", type="primary")
        
        if submit_button:
            nom = nom.strip()
            metier = metier.strip()
            commune = commune.strip()
            telephone = telephone.strip()
            
            if not nom or not metier or not commune or not telephone:
                st.error("⚠️ Tous les champs du formulaire doivent être remplis.")
            elif len(telephone) < 8:
                st.error("⚠️ Le numéro de téléphone est trop court pour être valide.")
            else:
                nouveau_prestataire = {
                    "nom": nom,
                    "metier": metier,
                    "commune": commune,
                    "appel_url": f"tel:{telephone}",
                    "whatsapp_url": f"https://wa.me/{telephone.replace('+', '').replace(' ', '')}"
                }
                
                artisans.append(nouveau_prestataire)
                with open("data.json", "w", encoding="utf-8") as f:
                    json.dump(artisans, f, ensure_ascii=False, indent=2)
                
                st.success("🎉 Établissement enregistré avec succès et validé !")

elif menu == "⚙️ Administration" and est_admin:
    st.subheader("🔐 Espace Administrateur Privé")
    st.success("Accès administrateur reconnu via l'URL sécurisée !")
    st.write(f"Nombre total d'établissements : **{len(artisans)}**")
    
    if artisans:
        st.markdown("---")
        st.subheader("Liste des prestataires à gérer :")
        
        for index, artisan in enumerate(artisans):
            col_info, col_btn = st.columns([3, 1])
            with col_info:
                st.write(f"**{artisan['nom']}** - {artisan['metier']} ({artisan['commune']})")
            with col_btn:
                if st.button("🗑️ Supprimer", key=f"suppr_{index}"):
                    artisans.pop(index)
                    with open("data.json", "w", encoding="utf-8") as f:
                        json.dump(artisans, f, ensure_ascii=False, indent=2)
                    st.success(f"'{artisan['nom']}' a été supprimé !")
                    st.rerun()
    else:
        st.info("Aucun prestataire à afficher.")
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
params = st.query_params
est_admin = params.get("admin") == "djassa_admin_secret_2026"

options_menu = ["🔍 Rechercher un prestataire", "📝 Enregistrer un établissement"]
if est_admin:
    options_menu.append("⚙️ Administration")

menu = st.sidebar.selectbox("Navigation", options_menu)

if menu == "🔍 Rechercher un prestataire":
    st.subheader("Espace de recherche")
    
    st.info(f"🔥 Déjà **{len(artisans)}** prestataire(s) et établissement(s) répertoriés sur la plateforme !")
    
    metier_cherche = st.text_input("Métier ou secteur recherché (ex: Plombier, Hôtel, Livreur)")
    
    st.write("**Ou filtrez rapidement par commune :**")
    cols_communes = st.columns(4)
    commune_selectionnee = ""
    
    communes_populaires = ["Cocody", "Yopougon", "Marcory", "Plateau"]
    for i, com in enumerate(communes_populaires):
        with cols_communes[i]:
            if st.button(com, use_container_width=True):
                commune_selectionnee = com

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
                # Récupération sécurisée des nouveaux champs (badge et description par défaut si absents)
                badge = artisan.get('badge', '⭐ Professionnel')
                description = artisan.get('description', 'Prestataire de confiance disponible sur Abidjan.')
                
                # Design de carte moderne et stylisé avec badges et descriptions
                with st.container():
                    st.markdown(
                        f"""
                        <div style="padding: 20px; border-radius: 10px; border: 1px solid #333333; margin-bottom: 10px; background-color: #1e1e1e;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <h3 style="margin: 0; color: #3b82f6;">{artisan['nom']}</h3>
                                <span style="background-color: #d97706; color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;">{badge}</span>
                            </div>
                            <p style="margin: 8px 0 5px 0; color: #e5e7eb;"><strong>{artisan['metier']}</strong> - 📍 {artisan['commune']}</p>
                            <p style="margin: 0 0 15px 0; color: #9ca3af; font-size: 14px;">{description}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f'<a href="{artisan["appel_url"]}" target="_self"><button style="background-color:#2563eb; color:white; padding:10px 16px; border:none; border-radius:6px; cursor:pointer; width:100%; font-weight:bold;">💬 Chat DJASSA</button></a>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<a href="{artisan["whatsapp_url"]}" target="_blank"><button style="background-color:#22c55e; color:white; padding:10px 16px; border:none; border-radius:6px; cursor:pointer; width:100%; font-weight:bold;">🟩 WhatsApp Direct</button></a>', unsafe_allow_html=True)
                
                texte_partage = urllib.parse.quote(f"Salut ! Je te partage ce contact trouvé sur DJASSA 🇨🇮 :\n*{artisan['nom']}* ({artisan['metier']}) à {artisan['commune']}.")
                st.markdown(f'<a href="https://wa.me/?text={texte_partage}" target="_blank"><button style="background-color:#0f766e; color:white; padding:8px 12px; border:none; border-radius:6px; cursor:pointer; width:100%; font-size:13px; margin-top:5px;">📤 Recommander ce prestataire sur WhatsApp</button></a>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.warning("Aucun prestataire trouvé pour ces critères.")
            
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
        description = st.text_area("Courte description des services proposés")
        badge = st.selectbox("Type de badge", ["⭐ Top Vendeur", "🛵 Livreur Pro", "⭐ Professionnel"])
        telephone = st.text_input("Numéro de téléphone (ex: +2250102030405)")
        
        submit_button = st.form_submit_button("Enregistrer l'établissement", type="primary")
        
        if submit_button:
            nom = nom.strip()
            metier = metier.strip()
            commune = commune.strip()
            description = description.strip()
            telephone = telephone.strip()
            
            if not nom or not metier or not commune or not description or not telephone:
                st.error("⚠️ Tous les champs du formulaire doivent être remplis.")
            elif len(telephone) < 8:
                st.error("⚠️ Le numéro de téléphone est trop court pour être valide.")
            else:
                nouveau_prestataire = {
                    "nom": nom,
                    "metier": metier,
                    "commune": commune,
                    "description": description,
                    "badge": badge,
                    "appel_url": f"tel:{telephone}",
                    "whatsapp_url": f"https://wa.me/{telephone.replace('+', '').replace(' ', '')}"
                }
                
                artisans.append(nouveau_prestataire)
                with open("data.json", "w", encoding="utf-8") as f:
                    json.dump(artisans, f, ensure_ascii=False, indent=2)
                
                st.success("🎉 Établissement enregistré avec succès et mis en page !")

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
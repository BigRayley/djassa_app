import json
import urllib.parse
import streamlit as st

st.set_page_config(page_title="DJASSA - Bêta", page_icon="🇨🇮", layout="centered")

# Chargement des prestataires depuis le fichier JSON
try:
    with open("data.json", "r", encoding="utf-8") as f:
        artisans = json.load(f)
except FileNotFoundError:
    artisans = []

# --- SECURITE ADMIN CACHEE PAR URL ---
params = st.query_params
est_admin = params.get("admin") == "djassa_admin_secret_2026"

# En-tête principal et Navigation horizontale moderne
st.title("🇨🇮 DJASSA")
st.write("La plateforme de référence pour trouver les meilleurs prestataires et services en Côte d'Ivoire.")

if est_admin:
    choix_menu = st.radio("Navigation", ["🔍 Rechercher un prestataire", "📝 Enregistrer un établissement", "⚙️ Administration & Modération"], horizontal=True)
else:
    choix_menu = st.radio("Navigation", ["🔍 Rechercher un prestataire", "📝 Enregistrer un établissement"], horizontal=True)

st.markdown("---")

if choix_menu == "🔍 Rechercher un prestataire":
    st.subheader("Espace de recherche")
    
    st.info(f"🔥 Déjà **{len(artisans)}** prestataire(s) et établissement(s) répertoriés sur la plateforme !")
    
    # --- NOUVEAU : Recherche directe par nom de service / établissement ---
    recherche_nom = st.text_input("🔍 Rechercher directement un nom d'établissement ou de service (ex: Chez Paul)", placeholder="Ex: Chez Paul, Maquis...")

    st.markdown("---")
    st.write("Ou utilisez les filtres par secteur :")
    
    # Extraction et séparation intelligente des secteurs/métiers uniques
    metiers_bruts = set()
    for artisan in artisans:
        metier_text = artisan.get('metier', '')
        for mot in metier_text.replace(" & ", " ").replace(" et ", " ").split():
            if len(mot) > 2:
                metiers_bruts.add(mot.capitalize())
        metiers_bruts.add(metier_text)

    metiers_disponibles = sorted(list(metiers_bruts))
    
    metier_selectionne = ""
    if metiers_disponibles:
        cols_metiers = st.columns(min(len(metiers_disponibles), 4))
        for i, met in enumerate(metiers_disponibles[:4]):
            with cols_metiers[i]:
                if st.button(met, use_container_width=True, key=f"btn_met_{i}"):
                    metier_selectionne = met

    metier_cherche = st.text_input("Métier ou secteur (ex: Hôtel, Boulangerie)", value=metier_selectionne)
    
    st.write("Ou filtrez par commune :")
    cols_communes = st.columns(4)
    commune_selectionnee = ""
    
    communes_populaires = ["Cocody", "Yopougon", "Marcory", "Plateau"]
    for i, com in enumerate(communes_populaires):
        with cols_communes[i]:
            if st.button(com, use_container_width=True, key=f"btn_com_{i}"):
                commune_selectionnee = com

    commune_cherche = st.text_input("Commune (ex: Cocody, Yopougon)", value=commune_selectionnee)

    if st.button("Lancer la recherche", type="primary"):
        resultats = []
        for artisan in artisans:
            # Si l'utilisateur tape un nom spécifique, on filtre en priorité sur le nom
            nom_match = recherche_nom.lower() in artisan['nom'].lower() if recherche_nom else True
            
            # Sinon on regarde les critères classiques métier et commune
            metier_match = metier_cherche.lower() in artisan['metier'].lower() if metier_cherche else True
            commune_match = commune_cherche.lower() in artisan['commune'].lower() if commune_cherche else True
            
            # Si une recherche par nom est active, elle prime, sinon on combine métier et commune
            if recherche_nom:
                if nom_match:
                    resultats.append(artisan)
            else:
                if metier_match and commune_match:
                    resultats.append(artisan)

        if resultats:
            st.success(f"{len(resultats)} prestataire(s) ou établissement(s) trouvé(s) !")
            for artisan in resultats:
                badge = artisan.get('badge', '⭐ Professionnel')
                description = artisan.get('description', 'Prestataire de confiance disponible sur Abidjan.')
                
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
            st.warning("Aucun établissement trouvé pour cette recherche.")
            
    st.markdown("---")
    st.subheader("🌟 Récemment ajoutés sur la plateforme")
    if artisans:
        derniers = artisans[-3:]
        for art in reversed(derniers):
            st.markdown(f"- **{art['nom']}** ({art['metier']}) à *{art['commune']}*")
    else:
        st.write("Aucun établissement pour le moment.")

elif choix_menu == "📝 Enregistrer un établissement":
    st.subheader("Enregistrer un nouveau prestataire ou établissement")
    
    with st.form("form_enregistrement"):
        nom = st.text_input("Nom de l'établissement ou de l'artisan (ex: Chez Paul)")
        metier = st.text_input("Métier ou secteur (ex: Boulangerie, Hôtel, Résidence)")
        commune = st.text_input("Commune (ex: Cocody, Yopougon, Marcory)")
        description = st.text_area("Courte description des services proposés (ex: Situé au Vallon)")
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
                
                st.success("🎉 Établissement enregistré avec succès !")

elif choix_menu == "⚙️ Administration & Modération" and est_admin:
    st.subheader("🔒 Administration & Modération DJASSA")
    st.info(f"📊 Total Établissements : {len(artisans)}")
    st.write("Gestion, Attribution de Badges & Suppression des Faux Profils :")
    
    if artisans:
        st.markdown("---")
        for index, artisan in enumerate(artisans):
            with st.container():
                st.markdown(
                    f"""
                    <div style="padding: 15px; border-radius: 8px; border: 1px solid #444; margin-bottom: 10px; background-color: #1e1e1e;">
                        <p style="margin: 0; color: #fff;"><strong>#{index+1} - {artisan['nom']}</strong> ({artisan['metier']} - {artisan['commune']})</p>
                        <p style="margin: 5px 0 0 0; font-size: 13px; color: #aaa;">Badge actuel : <strong>{artisan.get('badge', 'Professionnel')}</strong></p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            col_b, col_s = st.columns([2, 1])
            with col_b:
                nouveau_badge = st.selectbox("Modifier le badge", ["⭐ Top Vendeur", "🛵 Livreur Pro", "⭐ Professionnel"], key=f"badge_{index}")
                if st.button("Valider Badge", key=f"val_badge_{index}"):
                    artisans[index]['badge'] = nouveau_badge
                    with open("data.json", "w", encoding="utf-8") as f:
                        json.dump(artisans, f, ensure_ascii=False, indent=2)
                    st.success("Badge mis à jour avec succès !")
                    st.rerun()
            with col_s:
                if st.button("🗑️ Supprimer (Faux profil)", key=f"suppr_{index}", type="primary"):
                    artisans.pop(index)
                    with open("data.json", "w", encoding="utf-8") as f:
                        json.dump(artisans, f, ensure_ascii=False, indent=2)
                    st.success(f"'{artisan['nom']}' a été supprimé !")
                    st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("Aucun prestataire à modérer.")
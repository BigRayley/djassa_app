import urllib.parse
import streamlit as st
import streamlit.components.v1 as components
from database import get_connection, init_db, rechercher_artisans_intelligent

# Initialisation de la base de données SQLite
init_db()

st.set_page_config(page_title="DJASSA - Bêta", page_icon="🇨🇮", layout="centered")

# Chargement de tous les prestataires pour les statistiques et listes
def charger_tous_artisans():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nom, metier, commune, description, badge, appel_url, whatsapp_url FROM artisans")
    lignes = cursor.fetchall()
    conn.close()
    return [
        {
            "nom": r[0], "metier": r[1], "commune": r[2],
            "description": r[3], "badge": r[4], "appel_url": r[5], "whatsapp_url": r[6]
        } for r in lignes
    ]

tous_artisans = charger_tous_artisans()

# Initialisation des variables de session
if "resultats_recherche" not in st.session_state:
    st.session_state.resultats_recherche = None
if "appel_en_cours" not in st.session_state:
    st.session_state.appel_en_cours = None

# --- GESTION DE LA FIN D'APPEL DEPUIS LE BOUTON ROUGE ---
params = st.query_params
if "raccrocher" in params:
    st.session_state.appel_en_cours = None
    st.query_params.clear()
    st.rerun()

est_admin = params.get("admin") == "djassa_admin_secret_2026"

# En-tête principal et Navigation
st.title("🇨🇮 DJASSA")
st.write("La plateforme de référence pour trouver les meilleurs prestataires et services en Côte d'Ivoire.")

if est_admin:
    choix_menu = st.radio("Navigation", ["🔍 Rechercher un prestataire", "📝 Enregistrer un établissement", "⚙️ Administration & Modération"], horizontal=True)
else:
    choix_menu = st.radio("Navigation", ["🔍 Rechercher un prestataire", "📝 Enregistrer un établissement"], horizontal=True)

st.markdown("---")

if choix_menu == "🔍 Rechercher un prestataire":
    
    # --- INTERFACE D'APPEL INTERACTIVE ---
    if st.session_state.appel_en_cours:
        nom_appele = st.session_state.appel_en_cours
        
        html_appel = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    margin: 0; padding: 0; background-color: #0b0f19; color: white;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    display: flex; flex-direction: column; justify-content: space-between; align-items: center;
                    height: 100vh; box-sizing: border-box; padding: 40px 20px; overflow: hidden;
                }}
                .header-text {{ text-align: center; margin-top: 10px; }}
                .header-text h2 {{ font-size: 24px; font-weight: 500; margin: 0 0 8px 0; }}
                .header-text p {{ color: #9ca3af; font-size: 14px; letter-spacing: 1px; margin: 0; }}
                .avatar-container {{
                    width: 140px; height: 140px; background: linear-gradient(135deg, #0ea5e9, #f97316);
                    border-radius: 50%; display: flex; justify-content: center; align-items: center;
                    box-shadow: 0 0 35px rgba(14, 165, 233, 0.4);
                }}
                .avatar-inner {{
                    width: 124px; height: 124px; background-color: #0b0f19; border-radius: 50%;
                    display: flex; justify-content: center; align-items: center; font-size: 55px;
                }}
                .controls-bar {{ display: flex; justify-content: center; align-items: center; gap: 22px; margin-bottom: 20px; }}
                .control-btn {{
                    background-color: rgba(255, 255, 255, 0.12); width: 55px; height: 55px;
                    border-radius: 50%; display: flex; justify-content: center; align-items: center;
                    font-size: 22px; cursor: pointer; transition: all 0.2s;
                }}
                .control-btn:hover {{ background-color: rgba(255, 255, 255, 0.25); }}
                .control-btn.active {{ background-color: #3b82f6; }}
                .hangup-btn {{
                    background-color: #dc2626; width: 65px; height: 65px; border-radius: 50%;
                    display: flex; justify-content: center; align-items: center; font-size: 26px;
                    cursor: pointer; box-shadow: 0 4px 15px rgba(220, 38, 38, 0.5); transition: transform 0.2s;
                }}
                .hangup-btn:hover {{ transform: scale(1.05); }}
            </style>
        </head>
        <body>
            <div class="header-text">
                <h2>{nom_appele}</h2>
                <p id="status-text">⏳ Connexion audio en cours...</p>
            </div>
            <div class="avatar-container">
                <div class="avatar-inner">🛒</div>
            </div>
            <div class="controls-bar">
                <div class="control-btn" id="btn-fullscreen" onclick="toggleFullscreen()">↙↗</div>
                <div class="control-btn" id="btn-speaker" onclick="toggleSpeaker()">🔊</div>
                <div class="control-btn" id="btn-mic" onclick="toggleMic()">🔇</div>
                <div class="hangup-btn" onclick="window.location.href='?raccrocher=1'">📞</div>
            </div>
            <script>
                function toggleFullscreen() {{
                    if (!document.fullscreenElement) {{
                        document.documentElement.requestFullscreen().catch(err => {{}});
                        document.getElementById('btn-fullscreen').classList.add('active');
                    }} else {{
                        if (document.exitFullscreen) document.exitFullscreen();
                        document.getElementById('btn-fullscreen').classList.remove('active');
                    }}
                }}
                let speakerOn = false;
                function toggleSpeaker() {{
                    speakerOn = !speakerOn;
                    document.getElementById('btn-speaker').style.backgroundColor = speakerOn ? '#22c55e' : 'rgba(255, 255, 255, 0.12)';
                }}
                let micMuted = false;
                function toggleMic() {{
                    micMuted = !micMuted;
                    document.getElementById('btn-mic').style.backgroundColor = micMuted ? '#dc2626' : 'rgba(255, 255, 255, 0.12)';
                }}
            </script>
        </body>
        </html>
        """
        components.html(html_appel, height=600, scrolling=False)
        st.stop()

    # --- ESPACE DE RECHERCHE ---
    st.subheader("Espace de recherche")
    st.info(f"🔥 Déjà **{len(tous_artisans)}** prestataire(s) et établissement(s) répertoriés sur la plateforme !")
    
    # --- 1. RECHERCHE DIRECTE PAR NOM ---
    st.markdown("### 🎯 Recherche directe par nom d'établissement")
    with st.form("form_recherche_nom"):
        recherche_nom = st.text_input("Tapez le nom recherché (ex: Chez Paul)", placeholder="Ex: Chez Paul...")
        lancer_recherche_nom = st.form_submit_button("Rechercher par nom", type="primary")

    if lancer_recherche_nom and recherche_nom.strip():
        # Utilise la fonction SQL pour chercher spécifiquement
        st.session_state.resultats_recherche = rechercher_artisans_intelligent(query=recherche_nom.strip(), commune_filtre="")

    st.markdown("---")
    
    # --- 2. RECHERCHE PAR SECTEUR ET COMMUNE ---
    st.markdown("### 🔍 Ou filtrez par secteur et commune")
    
    # Nettoyage et normalisation des secteurs pour les suggestions
    metiers_bruts = set()
    for art in tous_artisans:
        metier_text = art.get('metier', '').strip().capitalize()
        if len(metier_text) > 2:
            metiers_bruts.add(metier_text)
    metiers_disponibles = sorted(list(metiers_bruts))
    
    if metiers_disponibles:
        st.write("💡 **Suggestions de secteurs populaires :**")
        cols_metiers = st.columns(min(len(metiers_disponibles), 4))
        for i, met in enumerate(metiers_disponibles[:4]):
            with cols_metiers[i]:
                if st.button(met, use_container_width=True, key=f"btn_met_{i}"):
                    st.session_state.resultats_recherche = rechercher_artisans_intelligent(query=met, commune_filtre="")

    communes_disponibles = ["Toutes les communes"] + sorted(list(set(art['commune'] for art in tous_artisans if art['commune'])))

    with st.form("form_recherche_criteres"):
        metier_cherche = st.text_input("Métier ou secteur (ex: Hôtel, Boulangerie)")
        commune_selectionnee = st.selectbox("📍 Filtrer par commune", communes_disponibles)
        lancer_recherche_criteres = st.form_submit_button("Lancer la recherche par critères", type="primary")

    if lancer_recherche_criteres:
        st.session_state.resultats_recherche = rechercher_artisans_intelligent(query=metier_cherche.strip(), commune_filtre=commune_selectionnee)

    # --- AFFICHAGE DES RÉSULTATS ---
    if st.session_state.resultats_recherche is not None:
        resultats = st.session_state.resultats_recherche
        if resultats:
            st.success(f"🎉 {len(resultats)} établissement(s) ou prestataire(s) trouvé(s) !")
            for index_art, artisan in enumerate(resultats):
                badge = artisan.get('badge', '⭐ Professionnel')
                description = artisan.get('description', 'Prestataire de confiance disponible sur Abidjan.')
                telephone_brut = artisan.get('appel_url', 'tel:+22500000000').replace('tel:', '')
                
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
                    st.markdown(f'<a href="{artisan["appel_url"]}" target="_self"><button style="background-color:#2563eb; color:white; padding:10px 16px; border:none; border-radius:6px; cursor:pointer; width:100%; font-weight:bold;">📞 {telephone_brut}</button></a>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<a href="{artisan["whatsapp_url"]}" target="_blank"><button style="background-color:#22c55e; color:white; padding:10px 16px; border:none; border-radius:6px; cursor:pointer; width:100%; font-weight:bold;">🟢 WhatsApp</button></a>', unsafe_allow_html=True)
                
                cle_appel = f"appel_smart_{index_art}"
                if st.button(f"🌐 Appel internet (Sans forfait) avec {artisan['nom']}", key=cle_appel, use_container_width=True):
                    st.session_state.appel_en_cours = artisan['nom']
                    st.rerun()

                texte_partage = urllib.parse.quote(f"Salut ! Je te partage ce contact trouvé sur DJASSA 🇨🇮 :\n*{artisan['nom']}* ({artisan['metier']}) à {artisan['commune']}.")
                st.markdown(f'<a href="https://wa.me/?text={texte_partage}" target="_blank"><button style="background-color:#0f766e; color:white; padding:8px 12px; border:none; border-radius:6px; cursor:pointer; width:100%; font-size:13px; margin-top:5px;">📤 Recommander ce prestataire sur WhatsApp</button></a>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.warning("Aucun établissement ou prestataire trouvé pour cette recherche.")
            
    st.markdown("---")
    st.subheader("🌟 Récemment ajoutés sur la plateforme")
    if tous_artisans:
        derniers = tous_artisans[-3:]
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
            metier = metier.strip().capitalize()
            commune = commune.strip().capitalize()
            description = description.strip()
            telephone = telephone.strip()
            
            if not nom or not metier or not commune or not description or not telephone:
                st.error("⚠️ Tous les champs du formulaire doivent être remplis.")
            elif len(telephone) < 8:
                st.error("⚠️ Le numéro de téléphone est trop court pour être valide.")
            else:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO artisans (nom, metier, commune, description, badge, appel_url, whatsapp_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (nom, metier, commune, description, badge, f"tel:{telephone}", f"https://wa.me/{telephone.replace('+', '').replace(' ', '')}"))
                conn.commit()
                conn.close()
                
                st.success("🎉 Établissement enregistré avec succès dans SQLite !")
                st.rerun()

elif choix_menu == "⚙️ Administration & Modération" and est_admin:
    st.subheader("🔒 Administration & Modération DJASSA")
    st.info(f"📊 Total Établissements : {len(tous_artisans)}")
    st.write("Gestion, Attribution de Badges & Suppression des Faux Profils :")
    
    if tous_artisans:
        st.markdown("---")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom, metier, commune, badge FROM artisans")
        db_artisans = cursor.fetchall()
        conn.close()
        
        for index, art_db in enumerate(db_artisans):
            art_id, art_nom, art_metier, art_commune, art_badge = art_db
            with st.container():
                st.markdown(
                    f"""
                    <div style="padding: 15px; border-radius: 8px; border: 1px solid #444; margin-bottom: 10px; background-color: #1e1e1e;">
                        <p style="margin: 0; color: #fff;"><strong>#{index+1} - {art_nom}</strong> ({art_metier} - {art_commune})</p>
                        <p style="margin: 5px 0 0 0; font-size: 13px; color: #aaa;">Badge actuel : <strong>{art_badge if art_badge else 'Professionnel'}</strong></p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            col_b, col_s = st.columns([2, 1])
            with col_b:
                nouveau_badge = st.selectbox("Modifier le badge", ["⭐ Top Vendeur", "🛵 Livreur Pro", "⭐ Professionnel"], key=f"badge_{art_id}")
                if st.button("Valider Badge", key=f"val_badge_{art_id}"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE artisans SET badge = ? WHERE id = ?", (nouveau_badge, art_id))
                    conn.commit()
                    conn.close()
                    st.success("Badge mis à jour avec succès dans SQLite !")
                    st.rerun()
            with col_s:
                if st.button("🗑️ Supprimer (Faux profil)", key=f"suppr_{art_id}", type="primary"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM artisans WHERE id = ?", (art_id,))
                    conn.commit()
                    conn.close()
                    st.success(f"'{art_nom}' a été supprimé de la base de données !")
                    st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("Aucun prestataire à modérer.")
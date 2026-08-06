import streamlit as st
import database
import requests
import os
import math
import streamlit.components.v1 as components
from streamlit_geolocation import streamlit_geolocation

# ==========================================
# 1. INITIALISATION DE LA BASE DE DONNÉES
# ==========================================
try:
    database.init_db()
except Exception as e:
    st.error(f"Erreur d'initialisation de la base de données : {e}")

# ==========================================
# 2. FONCTIONS UTILES (Paiement & Géolocalisation)
# ==========================================
def initialiser_paiement_fedapay(montant, description, nom_client, email_client):
    try:
        secret_key = st.secrets.get("FEDAPAY_SECRET_KEY") or os.getenv("FEDAPAY_SECRET_KEY")
    except Exception:
        secret_key = None

    if not secret_key:
        st.error("Clé FEDAPAY_SECRET_KEY introuvable dans secrets.toml")
        return None

    is_sandbox = secret_key.startswith("sk_sandbox") or "sandbox" in secret_key
    base_url = "https://sandbox-api.fedapay.com" if is_sandbox else "https://api.fedapay.com"

    url_transaction = f"{base_url}/v1/transactions"
    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "description": description,
        "amount": int(montant),
        "currency": {"iso": "XOF"},
        "customer": {"firstname": nom_client, "email": email_client}
    }

    try:
        response = requests.post(url_transaction, json=payload, headers=headers, timeout=10)
        data = response.json()
        if response.status_code in [200, 201]:
            trans_data = data.get("v1/transaction") or data.get("transaction") or data
            trans_id = trans_data.get("id")
            token_url = f"{base_url}/v1/transactions/{trans_id}/token"
            token_response = requests.post(token_url, headers=headers, timeout=10)
            return token_response.json().get("url")
        else:
            st.error(f"Erreur FedaPay : {data.get('message', 'Erreur de génération')}")
            return None
    except Exception as e:
        st.error(f"Erreur réseau : {e}")
        return None

def calculer_distance(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return None
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return round(R * c, 1)

# ==========================================
# 3. INTERFACE UTILISATEUR (DJASSA)
# ==========================================
def main():
    st.set_page_config(page_title="DJASSA", page_icon="🇨🇮", layout="wide")

    st.markdown("<h1 style='text-align: center; color: #ff6600;'>🇨🇮 DJASSA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Connectez-vous aux artisans, pharmacies et services en Côte d'Ivoire</p>", unsafe_allow_html=True)
    st.divider()

    st.write("**Navigation principale :**")
    menu = st.radio(
        "",
        ["🔍 Accueil / Recherche", "🏥 Pharmacies & Garde", "🌐 Passer Internet & Wave", "🛠️ Espace Prestataire", "👑 Espace Administrateur"],
        horizontal=True
    )
    st.divider()

    if menu == "🔍 Accueil / Recherche":
        st.title("🔍 Rechercher un service ou un artisan")
        
        st.write("📍 **Géolocalisation (optionnel pour trier par proximité) :**")
        loc = streamlit_geolocation()
        
        user_lat = loc.get('latitude') if loc else None
        user_lon = loc.get('longitude') if loc else None

        if user_lat and user_lon:
            st.success("Position GPS détectée avec succès !")

        st.divider()

        col1, col2, col3 = st.columns(3)
        with col1:
            query_finale = st.text_input("Nom de l'artisan / entreprise", placeholder="Ex: Kouassi...")
        with col2:
            commune = st.selectbox("Commune", ["Toutes les communes", "Cocody", "Yopougon", "Abobo", "Marcory", "Plateau"])
        with col3:
            service = st.selectbox("Service / Métier", ["Tous les services", "Plomberie", "Menuiserie", "Mécanique", "Électricité"])

        if st.button("Lancer la recherche", type="primary", use_container_width=True):
            st.session_state["recherche_lancee"] = True
            st.session_state["q_finale"] = query_finale
            st.session_state["q_commune"] = commune
            st.session_state["q_service"] = service

        if st.session_state.get("recherche_lancee"):
            artisans = database.rechercher_artisans_intelligent(
                st.session_state["q_finale"], 
                st.session_state["q_commune"], 
                st.session_state["q_service"]
            )
            
            if user_lat and user_lon and artisans:
                for art in artisans:
                    art['calculated_distance'] = calculer_distance(user_lat, user_lon, art.get('latitude'), art.get('longitude'))
                artisans = sorted(artisans, key=lambda x: x['calculated_distance'] if x['calculated_distance'] is not None else 9999)

            if artisans:
                st.success(f"{len(artisans)} artisan(s) trouvé(s) !")
                for art in artisans:
                    with st.expander(f"🛠️ {art['nom']} - {art['service']}"):
                        st.write(f"📍 **Commune :** {art['commune']}")
                        st.write(f"📞 **Téléphone :** {art['telephone']}")
                        st.write(f"📝 **Description :** {art['description']}")
                        
                        if user_lat and user_lon and art.get('calculated_distance') is not None:
                            st.info(f"🚗 **Distance :** Environ {art['calculated_distance']} km de votre position")

                        col_action1, col_action2 = st.columns(2)
                        with col_action1:
                            st.link_button(
                                f"📞 Appel opérateur ({art['telephone']})", 
                                f"tel:{art['telephone']}",
                                use_container_width=True
                            )
                        with col_action2:
                            cle_url = f"url_pay_{art['id']}"
                            if st.button(f"Payer un acompte (1000F)", key=f"btn_gen_{art['id']}", use_container_width=True):
                                with st.spinner("Génération FedaPay..."):
                                    url_paiement = initialiser_paiement_fedapay(
                                        montant=1000, 
                                        description=f"Acompte reservation {art['nom']}", 
                                        nom_client="Client Test", 
                                        email_client="contact@djassa.ci"
                                    )
                                    if url_paiement:
                                        st.session_state[cle_url] = url_paiement
                                    else:
                                        st.error("Échec génération lien.")

                        if cle_url in st.session_state:
                            st.link_button(
                                "💳 Procéder au paiement sécurisé", 
                                st.session_state[cle_url],
                                use_container_width=True
                            )

                        st.divider()

                        call_state_key = f"calling_{art['id']}"
                        if call_state_key not in st.session_state:
                            st.session_state[call_state_key] = False

                        if not st.session_state[call_state_key]:
                            if st.button(f"🎙️ Lancer un appel audio style WhatsApp avec {art['nom']}", key=f"start_call_{art['id']}", type="primary", use_container_width=True):
                                st.session_state[call_state_key] = True
                                st.rerun()
                        else:
                            whatsapp_call_html = f"""
                            <!DOCTYPE html>
                            <html lang="fr">
                            <head>
                                <meta charset="UTF-8">
                                <style>
                                    body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background-color: #111b21; font-family: sans-serif; }}
                                    .wa-call-screen {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: linear-gradient(135deg, #111b21 0%, #0b141a 100%); color: #ffffff; display: flex; flex-direction: column; justify-content: space-between; align-items: center; padding: 50px 20px; box-sizing: border-box; z-index: 999999; }}
                                    .wa-top-info {{ text-align: center; margin-top: 20px; }}
                                    .wa-avatar {{ width: 110px; height: 110px; background-color: #2a3942; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 50px; margin: 0 auto 20px auto; box-shadow: 0 0 0 10px rgba(42, 57, 66, 0.4); }}
                                    .wa-name {{ font-size: 28px; font-weight: 500; margin-bottom: 8px; }}
                                    .wa-status {{ font-size: 15px; color: #8696a0; }}
                                    .wa-encrypted {{ font-size: 12px; color: #8696a0; margin-bottom: 10px; opacity: 0.8; }}
                                    .wa-controls {{ display: flex; gap: 20px; align-items: center; background: rgba(34, 45, 52, 0.7); padding: 12px 25px; border-radius: 40px; margin-bottom: 30px; }}
                                    .wa-btn {{ width: 50px; height: 50px; border-radius: 50%; border: none; background-color: #2a3942; color: white; font-size: 20px; cursor: pointer; display: flex; align-items: center; justify-content: center; }}
                                    .wa-btn.active {{ background-color: #ffffff; color: #111b21; }}
                                    .wa-btn-hangup {{ width: 60px; height: 60px; background-color: #ea4335; font-size: 24px; }}
                                </style>
                            </head>
                            <body>
                                <div class="wa-call-screen">
                                    <div class="wa-top-info">
                                        <div class="wa-avatar">🛠️</div>
                                        <div class="wa-name">{art['nom']}</div>
                                        <div class="wa-status"><span id="timer">00:00</span></div>
                                    </div>
                                    <div class="wa-encrypted">🔒 Chiffré de bout en bout</div>
                                    <div class="wa-controls">
                                        <button class="wa-btn" id="btnMute" onclick="toggleMute()">🎤</button>
                                        <button class="wa-btn" id="btnSpeaker" onclick="toggleSpeaker()">🔊</button>
                                        <button class="wa-btn wa-btn-hangup" onclick="endCall()">📞</button>
                                    </div>
                                </div>
                                <script>
                                    let seconds = 0;
                                    setInterval(() => {{
                                        seconds++;
                                        let mins = Math.floor(seconds / 60).toString().padStart(2, '0');
                                        let secs = (seconds % 60).toString().padStart(2, '0');
                                        document.getElementById('timer').innerText = mins + ":" + secs;
                                    }}, 1000);
                                    let localStream = null;
                                    navigator.mediaDevices.getUserMedia({{ audio: true }}).then(stream => localStream = stream).catch(e => {{}});
                                    function toggleMute() {{
                                        if (!localStream) return;
                                        let enabled = localStream.getAudioTracks()[0].enabled;
                                        localStream.getAudioTracks()[0].enabled = !enabled;
                                        document.getElementById('btnMute').classList.toggle('active');
                                    }}
                                    function toggleSpeaker() {{ document.getElementById('btnSpeaker').classList.toggle('active'); }}
                                    function endCall() {{
                                        if (localStream) localStream.getTracks().forEach(t => t.stop());
                                        window.parent.location.reload();
                                    }}
                                </script>
                            </body>
                            </html>
                            """
                            components.html(whatsapp_call_html, height=720, scrolling=False)
                            if st.button("❌ Quitter l'interface d'appel", key=f"close_call_{art['id']}"):
                                st.session_state[call_state_key] = False
                                st.rerun()

                        st.divider()

                        with st.popover("💬 Envoyer un message ou demander un devis"):
                            st.write(f"Envoyer une demande à **{art['nom']}**")
                            with st.form(key=f"form_msg_{art['id']}"):
                                nom_c = st.text_input("Votre nom", key=f"nc_{art['id']}")
                                tel_c = st.text_input("Votre numéro de téléphone", key=f"tc_{art['id']}")
                                texte_msg = st.text_area("Votre message ou description du besoin", key=f"tm_{art['id']}")
                                if st.form_submit_button("Envoyer le message"):
                                    if nom_c and tel_c and texte_msg:
                                        database.envoyer_message_artisan(art['id'], nom_c, tel_c, texte_msg)
                                        st.success("Message envoyé avec succès !")
                                    else:
                                        st.error("Veuillez remplir tous les champs.")
            else:
                st.warning("Aucun artisan ne correspond à vos critères de recherche.")

    elif menu == "🏥 Pharmacies & Garde":
        st.title("🏥 Annuaire des Pharmacies d'Abidjan")
        st.write("Retrouvez toutes les pharmacies de la ville ou filtrez directement sur celles de garde.")
        
        col_ph1, col_ph2 = st.columns(2)
        with col_ph1:
            commune_pharmacie = st.selectbox("Filtrer par commune", ["Toutes les communes", "Cocody", "Yopougon", "Abobo", "Marcory", "Plateau"], key="commune_ph")
        with col_ph2:
            uniquement_garde = st.checkbox("🚨 Afficher uniquement les pharmacies de garde")

        pharmacies = database.obtenir_toutes_pharmacies(commune=commune_pharmacie, uniquement_garde=uniquement_garde)

        if pharmacies:
            st.success(f"{len(pharmacies)} pharmacie(s) trouvée(s) :")
            for ph in pharmacies:
                badge_garde = "🚨 **[DE GARDE]**" if ph['de_garde'] == 1 else "🟢 *Ouverte*"
                with st.expander(f"💊 {ph['nom']} ({ph['commune']}) - {badge_garde}"):
                    st.write(f"📍 **Adresse :** {ph['adresse']}")
                    st.write(f"📞 **Contact :** {ph['telephone']}")
                    st.link_button(f"📞 Appeler la pharmacie", f"tel:{ph['telephone']}")
        else:
            st.warning("Aucune pharmacie ne correspond à vos critères.")

    elif menu == "🌐 Passer Internet & Wave":
        st.title("🌐 Catalogue Complet des Offres Internet & Pass Spéciaux")
        st.write("Retrouvez l'ensemble des catalogues officiels des opérateurs en Côte d'Ivoire (Orange, MTN, Moov) incluant les pass spéciaux, et payez instantanément.")

        tab_net1, tab_net2 = st.tabs(["📶 Catalogue des Opérateurs & Pass Spéciaux", "🌊 Paiement & Transfert Wave"])

        with tab_net1:
            col_op_sel, col_cat_sel = st.columns(2)
            with col_op_sel:
                operateur_choisi = st.selectbox("Opérateur Télécom", ["Orange CI", "MTN CI", "Moov Africa CI"])
            with col_cat_sel:
                categorie_forfait = st.selectbox("Catégorie de Pass", [
                    "Pass Jour / Nuit (24h)", 
                    "Pass Semaine (3 à 7 jours)", 
                    "Pass Mois / Packs Mensuels", 
                    "Pass Spéciaux (Illimités, Nuit, Réseaux Sociaux & Étudiants)"
                ])

            # Catalogue structuré et exhaustif incluant les Pass Spéciaux
            catalogue_offres = {
                "Orange CI": {
                    "Pass Jour / Nuit (24h)": [
                        ("Pass 100F (80 Mo)", 100),
                        ("Pass 200F - 2 Jours (220 Mo)", 200),
                        ("Pass 300F - 3 Jours (340 Mo)", 300),
                        ("Pass 500F (750 Mo)", 500)
                    ],
                    "Pass Semaine (3 à 7 jours)": [
                        ("Pass Semaine 500F - Max It (1.5 Go)", 500),
                        ("Pass Semaine 1000F (1.5 Go + Bonus)", 1000),
                        ("Pass Semaine 1500F (2.5 Go + Bonus)", 1500)
                    ],
                    "Pass Mois / Packs Mensuels": [
                        ("Pass Mois 2500F (3.5 Go)", 2500),
                        ("Pass Mois 5000F (7.2 Go)", 5000),
                        ("Pass Mois 10000F (15 Go)", 10000),
                        ("Pass Mois 20000F (36 Go)", 20000)
                    ],
                    "Pass Spéciaux (Illimités, Nuit, Réseaux Sociaux & Étudiants)": [
                        ("Pass Nuit 250F (2 Go de 21h à 7h)", 250),
                        ("Pass Social 300F (WhatsApp / TikTok - 7 jours)", 300),
                        ("Pass Social Illimité 500F (24h - Tous réseaux)", 500),
                        ("Pass Étudiant / Campus 1000F (Accès illimité portails universitaires + 1 Go)", 1000),
                        ("Pass Web Illimité Weekend 2000F (Samedi & Dimanche)", 2000)
                    ]
                },
                "MTN CI": {
                    "Pass Jour / Nuit (24h)": [
                        ("Pass 150F (150 Mo)", 150),
                        ("Pass 200F (220 Mo)", 200),
                        ("Pass 300F (340 Mo)", 300),
                        ("Pass 500F (750 Mo)", 500)
                    ],
                    "Pass Semaine (3 à 7 jours)": [
                        ("Pass Semaine 1000F (1.2 Go)", 1000),
                        ("Pass Semaine 2000F (3.5 Go)", 2000)
                    ],
                    "Pass Mois / Packs Mensuels": [
                        ("Pack Mensuel 2500F (3.5 Go)", 2500),
                        ("Pack Mensuel 5000F (7.2 Go)", 5000),
                        ("Pack Mensuel 10000F (15 Go)", 10000),
                        ("Pack Mensuel 15000F (30 Go)", 15000)
                    ],
                    "Pass Spéciaux (Illimités, Nuit, Réseaux Sociaux & Étudiants)": [
                        ("Pass MTN Nuit 300F (3 Go de 00h à 6h)", 300),
                        ("Pass Social Jour 100F (WhatsApp / FB)", 100),
                        ("Pass Social Semaine 500F (TikTok / WhatsApp)", 500),
                        ("Pass Spécial Gamer 1500F (Optimisé jeux en ligne - 7 jours)", 1500),
                        ("Pass Illimité Mensuel 10000F (Réseaux sociaux illimités + 5Go)", 10000)
                    ]
                },
                "Moov Africa CI": {
                    "Pass Jour / Nuit (24h)": [
                        ("iZi'Free 100F (50 Mo)", 100),
                        ("iZi'Cool 200F (120 Mo)", 200),
                        ("Pass 300F (300 Mo)", 300),
                        ("Pass 500F (700 Mo)", 500)
                    ],
                    "Pass Semaine (3 à 7 jours)": [
                        ("Pass Semaine 1000F (1.5 Go)", 1000),
                        ("Pass Semaine 2000F (3 Go)", 2000)
                    ],
                    "Pass Mois / Packs Mensuels": [
                        ("Pass Mensuel 2500F (3.5 Go)", 2500),
                        ("Pass Mensuel 5000F (7.5 Go)", 5000),
                        ("Pass Mensuel 10000F (16 Go)", 10000)
                    ],
                    "Pass Spéciaux (Illimités, Nuit, Réseaux Sociaux & Étudiants)": [
                        ("Pass Moov Nuit 200F (1.5 Go de 23h à 6h)", 200),
                        ("Pass Social 150F (WhatsApp illimité 24h)", 150),
                        ("Pass Spécial Moov Flooz 600F (Semaine Sociale)", 600),
                        ("Pass Spécial Streaming 2500F (YouTube & Netflix dédiés - 7 jours)", 2500)
                    ]
                }
            }

            # Récupérer les options correspondantes
            offres_dispo = catalogue_offres.get(operateur_choisi, {}).get(categorie_forfait, [("Pass Standard 1000F", 1000)])

            st.markdown(f"### Offres pour **{operateur_choisi}** — *{categorie_forfait}*")
            
            choix_item = st.radio("Sélectionnez votre forfait ou pass spécial dans la liste :", [f"{item[0]} — {item[1]} FCFA" for item in offres_dispo])
            
            # Extraction propre du montant et du nom
            parts = choix_item.split("—")
            nom_pass = parts[0].strip()
            montant_pass = int(parts[1].replace("FCFA", "").strip())

            numero_a_recharger = st.text_input("Numéro de téléphone destinataire (ex: 07XXXXXXXX / 05XXXXXXXX / 01XXXXXXXX)")

            if st.button("Procéder à l'achat du pass", type="primary", use_container_width=True):
                if numero_a_recharger:
                    with st.spinner("Génération du guichet de paiement sécurisé (FedaPay)..."):
                        url_paiement_net = initialiser_paiement_fedapay(
                            montant=montant_pass,
                            description=f"Achat {nom_pass} ({operateur_choisi}) pour {numero_a_recharger}",
                            nom_client="Client DJASSA",
                            email_client="client@djassa.ci"
                        )
                        if url_paiement_net:
                            st.success("Lien de paiement généré avec succès !")
                            st.link_button("💳 Valider le paiement du pass", url_paiement_net, use_container_width=True)
                else:
                    st.error("Veuillez saisir un numéro de téléphone valide à recharger.")

        with tab_net2:
            st.subheader("Paiement rapide via Wave / Mobile Money")
            st.write("Effectuez un règlement direct par passerelle sécurisée.")
            
            montant_wave = st.number_input("Montant en FCFA", min_value=100, step=500, value=1000)
            motif_wave = st.text_input("Motif du paiement ou transfert", placeholder="Ex: Achat marchand, service...")
            
            if st.button("Générer le lien de paiement Wave / FedaPay", type="primary", use_container_width=True):
                with st.spinner("Création de la transaction..."):
                    url_w = initialiser_paiement_fedapay(
                        montant=montant_wave,
                        description=f"Paiement Wave/Mobile : {motif_wave}",
                        nom_client="Client Wave",
                        email_client="wave@djassa.ci"
                    )
                    if url_w:
                        st.success("Guichet prêt !")
                        st.link_button("🌊 Ouvrir le guichet de paiement", url_w, use_container_width=True)

    elif menu == "🛠️ Espace Prestataire":
        st.title("🛠️ Espace Prestataire - Inscription")
        st.write("Vous êtes artisan ou prestataire à Abidjan ? Enregistrez vos services pour apparaître dans l'annuaire DJASSA.")
        
        with st.form("form_inscription_artisan"):
            nom_artisan = st.text_input("Nom de l'entreprise ou de l'artisan")
            commune_artisan = st.selectbox("Commune principale", ["Cocody", "Yopougon", "Abobo", "Marcory", "Plateau"])
            service_artisan = st.selectbox("Votre corps de métier / Service", ["Plomberie", "Menuiserie", "Mécanique", "Électricité"])
            telephone_artisan = st.text_input("Numéro de téléphone (ex: 0700000000)")
            description_artisan = st.text_area("Description de vos prestations")
            
            if st.form_submit_button("S'inscrire sur DJASSA", type="primary"):
                if nom_artisan and telephone_artisan and description_artisan:
                    database.ajouter_artisan(nom_artisan, commune_artisan, service_artisan, telephone_artisan, description_artisan)
                    st.success("🎉 Profil enregistré avec succès !")
                else:
                    st.error("Veuillez remplir tous les champs obligatoires.")

    elif menu == "👑 Espace Administrateur":
        st.title("👑 Espace Administrateur DJASSA")
        mdp = st.text_input("Mot de passe administrateur", type="password")
        
        if mdp == "admin123":
            st.success("Connexion réussie !")
            
            tous_artisans = database.obtenir_tous_artisans()
            toutes_pharmacies = database.obtenir_toutes_pharmacies()
            tous_messages = database.obtenir_tous_les_messages()
            
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric(label="Artisans inscrits", value=len(tous_artisans))
            with col_stat2:
                st.metric(label="Pharmacies", value=len(toutes_pharmacies))
            with col_stat3:
                st.metric(label="Messages reçus", value=len(tous_messages))

            st.divider()
            tab_admin1, tab_admin2, tab_admin3 = st.tabs(["📋 Gérer les Artisans", "💊 Gérer les Pharmacies", "💬 Boîte de réception (Messages)"])
            
            with tab_admin1:
                st.subheader("Liste des artisans")
                if tous_artisans:
                    for art in tous_artisans:
                        col_info, col_action = st.columns([4, 1])
                        with col_info:
                            st.write(f"**{art['nom']}** ({art['service']} - {art['commune']})")
                        with col_action:
                            if st.button("❌ Supprimer", key=f"del_art_{art['id']}"):
                                database.supprimer_artisan(art['id'])
                                st.rerun()
                else:
                    st.info("Aucun artisan.")

            with tab_admin2:
                st.subheader("Modifier les pharmacies de garde")
                for ph in toutes_pharmacies:
                    col_pinfo, col_pbtn = st.columns([3, 2])
                    with col_pinfo:
                        statut_txt = "🚨 De Garde" if ph['de_garde'] == 1 else "Standard"
                        st.write(f"**{ph['nom']}** ({ph['commune']}) — *{statut_txt}*")
                    with col_pbtn:
                        nouveau_etat = st.selectbox(
                            "Statut", [0, 1], index=ph['de_garde'], key=f"garde_{ph['id']}",
                            format_func=lambda x: "De Garde 🚨" if x == 1 else "Standard 🟢"
                        )
                        if nouveau_etat != ph['de_garde']:
                            database.basculer_statut_garde(ph['id'], nouveau_etat)
                            st.success(f"Statut mis à jour pour {ph['nom']} !")
                            st.rerun()

            with tab_admin3:
                st.subheader("Messages et demandes reçus des clients")
                if tous_messages:
                    for msg in tous_messages:
                        with st.expander(f"📩 Message de {msg['nom_client']} pour {msg['nom_artisan']} ({msg['date_envoi']})"):
                            st.write(f"📞 **Téléphone du client :** {msg['telephone_client']}")
                            st.write(f"📝 **Contenu :** {msg['contenu_message']}")
                            st.link_button("Rappeler le client", f"tel:{msg['telephone_client']}")
                else:
                    st.info("Aucun message reçu pour le moment.")

        elif mdp:
            st.error("Mot de passe incorrect.")

    else:
        st.info("Cette section est en cours de développement.")

if __name__ == "__main__":
    main()
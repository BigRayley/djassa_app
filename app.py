import streamlit as st
import database
import requests
import os

# ==========================================
# 1. INITIALISATION DE LA BASE DE DONNÉES
# ==========================================
try:
    # On lance l'initialisation dès le démarrage
    database.init_db()
except Exception as e:
    st.error(f"Erreur d'initialisation de la base de données : {e}")

# ==========================================
# 2. FONCTION DE PAIEMENT FEDAPAY
# ==========================================
def initialiser_paiement_fedapay(montant, description, nom_client, email_client):
    try:
        secret_key = st.secrets.get("FEDAPAY_SECRET_KEY") or os.getenv("FEDAPAY_SECRET_KEY")
    except Exception:
        secret_key = None

    if not secret_key:
        st.error("Clé FEDAPAY_SECRET_KEY introuvable dans secrets.toml")
        return None

    # Détection automatique du mode Live ou Sandbox
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


# ==========================================
# 3. INTERFACE UTILISATEUR (DJASSA)
# ==========================================
def main():
    # Configuration de la page
    st.set_page_config(page_title="DJASSA", page_icon="🇨🇮", layout="wide")

    # En-tête
    st.markdown("<h1 style='text-align: center; color: #ff6600;'>🇨🇮 DJASSA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Connectez-vous aux artisans, pharmacies et services en Côte d'Ivoire</p>", unsafe_allow_html=True)
    st.divider()

    # Menu de navigation
    st.write("**Navigation principale :**")
    menu = st.radio(
        "",
        ["🔍 Accueil / Recherche", "🏥 Pharmacies de Garde", "🌐 Passer Internet & Wave", "🛠️ Espace Prestataire", "👑 Espace Administrateur"],
        horizontal=True
    )
    st.divider()

    # SECTION : ACCUEIL / RECHERCHE
    if menu == "🔍 Accueil / Recherche":
        st.title("🔍 Rechercher un service ou un artisan")
        
        # Filtres de recherche
        col1, col2, col3 = st.columns(3)
        with col1:
            query_finale = st.text_input("Nom de l'artisan / entreprise", placeholder="Ex: Kouassi...")
        with col2:
            commune = st.selectbox("Commune", ["Toutes les communes", "Cocody", "Yopougon", "Abobo", "Marcory", "Plateau"])
        with col3:
            service = st.selectbox("Service / Métier", ["Tous les services", "Plomberie", "Menuiserie", "Mécanique", "Électricité"])

        # Bouton pour lancer la recherche
        if st.button("Lancer la recherche", type="primary", use_container_width=True):
            # On mémorise dans st.session_state que la recherche a été activée
            st.session_state["recherche_lancee"] = True
            st.session_state["q_finale"] = query_finale
            st.session_state["q_commune"] = commune
            st.session_state["q_service"] = service

        # On affiche les résultats SEULEMENT si la recherche a été lancée au moins une fois
        if st.session_state.get("recherche_lancee"):
            artisans = database.rechercher_artisans_intelligent(
                st.session_state["q_finale"], 
                st.session_state["q_commune"], 
                st.session_state["q_service"]
            )
            
            if artisans:
                st.success(f"{len(artisans)} artisan(s) trouvé(s) !")
                for art in artisans:
                    with st.expander(f"🛠️ {art['nom']} - {art['service']}"):
                        st.write(f"📍 **Commune :** {art['commune']}")
                        st.write(f"📞 **Téléphone :** {art['telephone']}")
                        st.write(f"📝 **Description :** {art['description']}")
                        
                        cle_url = f"url_pay_{art['id']}"
                        
                        # Bouton qui génère le paiement
                        if st.button(f"Payer un acompte à {art['nom']} (1000 FCFA)", key=f"btn_gen_{art['id']}"):
                            with st.spinner("Génération du guichet de paiement FedaPay..."):
                                url_paiement = initialiser_paiement_fedapay(
                                    montant=1000, 
                                    description=f"Acompte reservation {art['nom']}", 
                                    nom_client="Client Test", 
                                    email_client="contact@djassa.ci"
                                )
                                if url_paiement:
                                    # On stocke l'URL de paiement générée dans le state
                                    st.session_state[cle_url] = url_paiement
                                else:
                                    st.error("Échec de la génération du lien. Vérifie ta clé Sandbox.")
                        
                        # Affichage du bouton de redirection vers FedaPay si le lien a été généré
                        if cle_url in st.session_state:
                            st.success("Lien de paiement généré avec succès !")
                            st.link_button(
                                "💳 Accéder au guichet de paiement (FedaPay)", 
                                st.session_state[cle_url],
                                use_container_width=True
                            )
            else:
                st.warning("Aucun artisan ne correspond à vos critères de recherche.")

    # AUTRES SECTIONS
    elif menu == "🛠️ Espace Prestataire":
        st.info("Cette section permettra aux artisans de s'inscrire et gérer leur profil.")
    else:
        st.info("Cette section est en cours de développement.")

if __name__ == "__main__":
    main()
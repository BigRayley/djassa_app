import json
import streamlit as st

st.set_page_config(page_title="DJASSA", page_icon="🇨🇮")

st.title("🇨🇮 DJASSA - Application des Artisans")
st.write("Trouvez les meilleurs prestataires de services près de chez vous en Côte d'Ivoire.")

# Chargement des artisans depuis le fichier JSON
try:
    with open("data.json", "r", encoding="utf-8") as f:
        artisans = json.load(f)
except FileNotFoundError:
    artisans = []

# Barre de recherche
metier_cherche = st.text_input("Métier recherché (ex: Électricien, Plombier)")
commune_cherche = st.text_input("Commune (ex: Cocody, Yopougon)")

if st.button("Lancer la recherche"):
# Filtrage insensible à la casse
    for artisan in artisans:
        metier_match = metier_cherche.lower() in artisan['metier'].lower() if metier_cherche else True
        commune_match = commune_cherche.lower() in artisan['commune'].lower() if commune_cherche else True
        
        if metier_match and commune_match:
            resultats.append(artisan)
        metier_match = metier_cherche.lower() in artisan['metier'].lower() if metier_cherche else True
        commune_match = commune_cherche.lower() in artisan['commune'].lower() if commune_cherche else True
        
        if metier_match and commune_match:
            resultats.append(artisan)
            
    if resultats:
        st.success(f"{len(resultats)} prestataire(s) trouvé(s) !")
        for artisan in resultats:
            st.markdown(f"---")
            st.subheader(f"{artisan['nom']}")
            st.write(f"**Métier :** {artisan['metier']}")
            st.write(f"**Commune :** {artisan['commune']}")
            
            # Gestion des boutons de contact
            telephone = artisan.get("telephone", "")
            if telephone:
                whatsapp_url = f"https://wa.me/{telephone}"
                appel_url = f"tel:{telephone}"
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f'<a href="{appel_url}" target="_self"><button style="width:100%; background-color:#4CAF50; color:white; padding:8px; border:none; border-radius:5px; cursor:pointer;">📞 Appeler</button></a>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; padding:8px; border:none; border-radius:5px; cursor:pointer;">💬 WhatsApp</button></a>', unsafe_allow_html=True)
    else:
        st.warning("Aucun artisan trouvé pour ces critères.")
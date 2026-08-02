import json
import os

FICHIER_DONNEES = "artisans.json"

class Artisan:
    def __init__(self, nom, prenom, telephone, commune, metier, est_verifie=False, id_user=None, note=5.0, nombre_avis=0, categorie="Général"):
        self.id_user = id_user
        self.nom = nom
        self.prenom = prenom
        self.telephone = telephone
        self.commune = commune
        self.metier = metier
        self.est_verifie = est_verifie
        self.note = note
        self.nombre_avis = nombre_avis
        self.categorie = categorie

    def to_dict(self):
        return {
            "id_user": self.id_user,
            "nom": self.nom,
            "prenom": self.prenom,
            "telephone": self.telephone,
            "commune": self.commune,
            "metier": self.metier,
            "est_verifie": self.est_verifie,
            "note": self.note,
            "nombre_avis": self.nombre_avis,
            "categorie": self.categorie
        }

def charger_artisans():
    if os.path.exists(FICHIER_DONNEES):
        with open(FICHIER_DONNEES, "r", encoding="utf-8") as f:
            data = json.load(f)
            artisans = []
            for item in data:
                if "note" not in item:
                    item["note"] = 5.0
                if "nombre_avis" not in item:
                    item["nombre_avis"] = 0
                if "categorie" not in item:
                    item["categorie"] = "Général"
                artisans.append(Artisan(**item))
            return artisans
    return []

def sauvegarder_artisans(liste_artisans):
    with open(FICHIER_DONNEES, "w", encoding="utf-8") as f:
        json.dump([art.to_dict() for art in liste_artisans], f, indent=4, ensure_ascii=False)
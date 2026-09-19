"""Catalogue explicite des statistiques autorisées par l'application."""

SOURCES = {
    "locations": {"label": "Locations", "measures": {"nombre_emprunts": "Nombre d'emprunts", "duree_totale": "Durée totale (semaines)", "duree_moyenne": "Durée moyenne (semaines)"}, "dimensions": {"materiel": "Matériel", "categorie": "Catégorie", "mois_debut": "Mois de début", "statut": "Statut de l'emprunt"}, "filters": {"periode": True, "categorie": True, "statut": True}},
    "recettes": {"label": "Recettes", "measures": {"recettes_total": "Recettes totales (€)", "recette_moyenne": "Recette moyenne (€)", "nombre_emprunts": "Nombre d'emprunts encaissés"}, "dimensions": {"materiel": "Matériel", "categorie": "Catégorie", "mois_retour": "Mois de retour", "type_paiement": "Moyen de paiement"}, "filters": {"periode": True, "categorie": True, "type_paiement": True}},
    "parc": {"label": "État du parc", "measures": {"nombre_materiels": "Nombre de matériels", "valeur_achat": "Valeur d'achat cumulée (€)", "heures_utilisation": "Heures d'utilisation cumulées"}, "dimensions": {"categorie": "Catégorie", "etat": "État", "marque": "Marque", "type_energie": "Type d'énergie"}, "filters": {"categorie": True, "etat": True}},
}


def catalog_for_browser():
    return SOURCES


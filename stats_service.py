"""Requêtes de statistiques composées uniquement avec le catalogue autorisé."""
from datetime import date
from sqlalchemy import func
from models import Emprunt, Materiel, Statut_Emprunt
from stats_catalog import SOURCES


class StatisticsValidationError(ValueError):
    pass


def _date(value, label):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as error:
        raise StatisticsValidationError(f"{label} doit être au format AAAA-MM-JJ.") from error


def _validate(configuration):
    source = configuration.get("source")
    if source not in SOURCES:
        raise StatisticsValidationError("Source de données inconnue.")
    measure, dimension = configuration.get("measure"), configuration.get("dimension") or None
    if measure not in SOURCES[source]["measures"]:
        raise StatisticsValidationError("Mesure non disponible pour cette source.")
    if dimension and dimension not in SOURCES[source]["dimensions"]:
        raise StatisticsValidationError("Répartition non disponible pour cette source.")
    return source, measure, dimension, configuration.get("filters") or {}


def _serialize(query, dimension, label):
    rows = query.all()
    if dimension:
        labels, values = [getattr(row[0], "value", row[0]) or "Non renseigné" for row in rows], [float(row[1] or 0) for row in rows]
    else:
        labels, values = [label], [float(rows[0][0] or 0) if rows else 0]
    return {"labels": labels, "datasets": [{"label": label, "data": values}], "table": [{"libelle": key, "valeur": value} for key, value in zip(labels, values)]}


def _emprunts(measure, dimension, filters, recettes=False):
    metrics = ({"recettes_total": func.coalesce(func.sum(Emprunt.montant_paye), 0), "recette_moyenne": func.coalesce(func.avg(Emprunt.montant_paye), 0), "nombre_emprunts": func.count(Emprunt.id_emprunt)} if recettes else {"nombre_emprunts": func.count(Emprunt.id_emprunt), "duree_totale": func.coalesce(func.sum(Emprunt.duree), 0), "duree_moyenne": func.coalesce(func.avg(Emprunt.duree), 0)})
    dimensions = ({"materiel": Materiel.nom_materiel, "categorie": Materiel.categorie, "mois_retour": func.strftime("%Y-%m", Emprunt.date_retour_effective), "type_paiement": Emprunt.type_paiement} if recettes else {"materiel": Materiel.nom_materiel, "categorie": Materiel.categorie, "mois_debut": func.strftime("%Y-%m", Emprunt.date_debut), "statut": Emprunt.statut})
    query = Emprunt.query.join(Materiel)
    date_field = Emprunt.date_retour_effective if recettes else Emprunt.date_debut
    if recettes:
        query = query.filter(Emprunt.statut == Statut_Emprunt.retourne, Emprunt.date_retour_effective.isnot(None), Emprunt.montant_paye.isnot(None))
    start, end = _date(filters.get("date_debut"), "La date de début"), _date(filters.get("date_fin"), "La date de fin")
    if start: query = query.filter(date_field >= start)
    if end: query = query.filter(date_field <= end)
    if filters.get("categorie"): query = query.filter(Materiel.categorie == filters["categorie"])
    if filters.get("statut") and not recettes: query = query.filter(Emprunt.statut == filters["statut"])
    if filters.get("type_paiement") and recettes: query = query.filter(Emprunt.type_paiement == filters["type_paiement"])
    metric = metrics[measure].label("valeur")
    if dimension:
        field = dimensions[dimension]
        query = query.with_entities(field.label("libelle"), metric).group_by(field).order_by(field)
    else: query = query.with_entities(metric)
    source = "recettes" if recettes else "locations"
    return _serialize(query, dimension, SOURCES[source]["measures"][measure])


def _parc(measure, dimension, filters):
    metrics = {"nombre_materiels": func.count(Materiel.id_materiel), "valeur_achat": func.coalesce(func.sum(Materiel.prix_achat), 0), "heures_utilisation": func.coalesce(func.sum(Materiel.nb_heure), 0)}
    dimensions = {"categorie": Materiel.categorie, "etat": Materiel.etat, "marque": Materiel.marque, "type_energie": Materiel.type_energie}
    query = Materiel.query
    if filters.get("categorie"): query = query.filter(Materiel.categorie == filters["categorie"])
    if filters.get("etat"): query = query.filter(Materiel.etat == filters["etat"])
    metric = metrics[measure].label("valeur")
    if dimension:
        field = dimensions[dimension]
        query = query.with_entities(field.label("libelle"), metric).group_by(field).order_by(field)
    else: query = query.with_entities(metric)
    return _serialize(query, dimension, SOURCES["parc"]["measures"][measure])


def preview(configuration):
    source, measure, dimension, filters = _validate(configuration)
    if source == "locations": result = _emprunts(measure, dimension, filters)
    elif source == "recettes": result = _emprunts(measure, dimension, filters, recettes=True)
    else: result = _parc(measure, dimension, filters)
    result["title"] = SOURCES[source]["measures"][measure]
    return result


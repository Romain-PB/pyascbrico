"""Tests de non-régression des fonctions présentes avant le module Statistiques."""

import pytest

from app import app
from models import Adherent, Consommable, db


@pytest.mark.parametrize("path", [
    "/", "/materiels", "/materiels/create", "/materiels/1",
    "/adherents", "/adherents/1", "/adherents/add", "/consommables",
    "/pannes", "/recettes", "/emprunts", "/emprunts/historique",
])
def test_existing_pages_render(path, client):
    """Les pages historiques essentielles restent accessibles après un ajout."""
    assert client.get(path).status_code == 200


def test_member_can_still_be_added(client):
    response = client.post("/adherents/add", data={
        "numero_asc": "42", "nom": "Dupont", "prenom": "Camille",
        "email": "camille.dupont@test.local", "telephone": "0102030405", "portable": "0601020304",
    })
    assert response.status_code == 302
    with app.app_context():
        assert Adherent.query.filter_by(numero_asc=42).one().prenom == "Camille"


def test_consumable_can_still_be_added(client):
    response = client.post("/consommables", data={
        "nom_consommable": "Foret béton", "description": "Test non-régression",
        "quantite_disponible": "4", "prix": "6.5",
    })
    assert response.status_code == 302
    with app.app_context():
        consumable = Consommable.query.filter_by(nom_consommable="Foret béton").one()
        assert consumable.quantite_disponible == 4
        assert consumable.prix == 6.5


def test_get_requests_do_not_modify_the_database(client):
    with app.app_context():
        before = (Adherent.query.count(), Consommable.query.count())
    for path in ["/materiels", "/adherents", "/consommables", "/emprunts", "/stats"]:
        assert client.get(path).status_code == 200
    with app.app_context():
        assert (Adherent.query.count(), Consommable.query.count()) == before


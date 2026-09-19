import os
from datetime import date
os.environ["ASC_BRICOLAGE_DATABASE_URI"] = "sqlite:///:memory:"

import pytest
from app import app
from models import Adherent, Categorie, Emprunt, Etat, Materiel, Statut_Emprunt, TypeEnergie, Type_Paiement, db


@pytest.fixture(autouse=True)
def database():
    with app.app_context():
        db.create_all()
        adherent = Adherent(numero_asc=1, nom="Test", prenom="Alice", email="alice@test.local", valide_asc=True)
        perceuse = Materiel(numero_materiel=1, nom_materiel="Perceuse", prix_location_semaine=10, categorie=Categorie.batiment, etat=Etat.ok, type_energie=TypeEnergie.batterie, prix_achat=100, nb_heure=5)
        tondeuse = Materiel(numero_materiel=2, nom_materiel="Tondeuse", prix_location_semaine=20, categorie=Categorie.jardinage, etat=Etat.en_panne, type_energie=TypeEnergie.thermique, prix_achat=300, nb_heure=10)
        db.session.add_all([adherent, perceuse, tondeuse]); db.session.flush()
        db.session.add_all([Emprunt(date_debut=date(2026, 1, 3), duree=2, statut=Statut_Emprunt.retourne, id_materiel=perceuse.id_materiel, id_adherent=adherent.id_adherent, date_retour_effective=date(2026, 1, 17), montant_paye=20, type_paiement=Type_Paiement.CB), Emprunt(date_debut=date(2026, 2, 3), duree=1, statut=Statut_Emprunt.reserve, id_materiel=tondeuse.id_materiel, id_adherent=adherent.id_adherent), Emprunt(date_debut=date(2026, 9, 18), duree=2, statut=Statut_Emprunt.en_cours, id_materiel=perceuse.id_materiel, id_adherent=adherent.id_adherent)])
        db.session.commit(); yield
        db.session.remove(); db.drop_all()


@pytest.fixture
def client():
    return app.test_client()


"""Crée une base de démonstration déterministe, distincte de la base courante."""
import os
import sys
import random
from datetime import date, timedelta

os.environ.setdefault("ASC_BRICOLAGE_DATABASE_URI", "sqlite:///demo.db")

from app import app
from models import Adherent, Categorie, Emprunt, Etat, Materiel, Statut_Emprunt, TypeEnergie, Type_Paiement, db


def seed():
    with app.app_context():
        db.drop_all(); db.create_all()
        rng = random.Random(20260919)
        prenoms = ["Alice", "Bruno", "Chloé", "David", "Emma", "François", "Gaëlle", "Hugo", "Inès", "Julien", "Karim", "Laura", "Marc", "Nadia", "Olivier", "Pauline", "Quentin", "Rania", "Sophie", "Thomas", "Ulysse", "Valérie", "William", "Xavier", "Yasmine", "Zoé", "Antoine", "Béatrice", "Cédric", "Delphine"]
        noms = ["Martin", "Durand", "Bernard", "Petit", "Robert", "Richard", "Moreau", "Simon", "Laurent", "Lefèvre"]
        adherents = [Adherent(numero_asc=index + 1, nom=noms[index % len(noms)], prenom=prenom, email=f"{prenom.lower()}.{index + 1}@example.test", valide_asc=True, statut="Adhérent ASC", depuis=date(2022 + index % 4, 1 + index % 12, 1)) for index, prenom in enumerate(prenoms)]
        db.session.add_all(adherents)

        prefixes = {Categorie.automobile: "Clé à filtre", Categorie.bois: "Scie", Categorie.batiment: "Perceuse", Categorie.divers: "Escabeau", Categorie.plomberie: "Déboucheur", Categorie.tapisserie: "Décolleuse", Categorie.jardinage: "Tondeuse"}
        materiels = []
        for index in range(120):
            categorie = list(Categorie)[index % len(Categorie)]
            etat = Etat.ok if index % 12 else Etat.en_panne if index % 24 else Etat.reforme
            materiels.append(Materiel(numero_materiel=1001 + index, nom_materiel=f"{prefixes[categorie]} {index + 1:03d}", prix_location_semaine=round(rng.uniform(8, 65), 2), categorie=categorie, etat=etat, type_energie=rng.choice(list(TypeEnergie)), prix_achat=round(rng.uniform(40, 1800), 2), nb_heure=rng.randint(0, 900), marque=rng.choice(["Bosch", "Makita", "Stihl", "Ryobi", "Facom", "Einhell"]), localisation=f"Rayon {1 + index % 8}"))
        db.session.add_all(materiels); db.session.flush()

        # Chaque intervalle inclut un éventuel retard : un matériel ne peut donc
        # jamais être attribué à deux adhérents pendant la même période.
        occupations = {materiel.id_materiel: [] for materiel in materiels}

        def disponible(materiel, debut, fin):
            return all(fin <= occ_debut or debut >= occ_fin for occ_debut, occ_fin in occupations[materiel.id_materiel])

        def reserver(materiel, debut, fin):
            occupations[materiel.id_materiel].append((debut, fin))

        emprunts = []
        aujourd_hui = date.today()
        # Les emprunts historiques sont tous clôturés.  Un retard ajoute une ou
        # deux semaines complètes, jamais quelques jours seulement.
        fin_historique = aujourd_hui - timedelta(days=28)
        debut_historique = date(2024, 1, 1)
        for _ in range(680):
            for _tentative in range(500):
                materiel = rng.choice(materiels)
                adherent = rng.choice(adherents)
                duree = rng.choice([1, 2])
                retard_semaines = rng.choices([0, 1, 2], weights=[86, 11, 3])[0]
                date_debut = debut_historique + timedelta(days=rng.randrange((fin_historique - debut_historique).days - 28))
                date_retour = date_debut + timedelta(weeks=duree + retard_semaines)
                if disponible(materiel, date_debut, date_retour):
                    reserver(materiel, date_debut, date_retour)
                    emprunts.append(Emprunt(date_debut=date_debut, duree=duree, statut=Statut_Emprunt.retourne, id_materiel=materiel.id_materiel, id_adherent=adherent.id_adherent, date_retour_effective=date_retour, montant_paye=round(materiel.prix_location_semaine * (duree + retard_semaines), 2), type_paiement=rng.choice(list(Type_Paiement)), consommables_ids="[]"))
                    break
            else:
                raise RuntimeError("Impossible de planifier un emprunt historique sans chevauchement.")

        # Emprunts en cours et réservations : au plus trois semaines avant leur début.
        for _ in range(18):
            for _tentative in range(200):
                materiel, adherent = rng.choice(materiels), rng.choice(adherents)
                duree, date_debut = rng.choice([1, 2]), aujourd_hui - timedelta(days=rng.randrange(0, 13))
                date_fin_prevue = date_debut + timedelta(weeks=duree)
                if disponible(materiel, date_debut, date_fin_prevue):
                    reserver(materiel, date_debut, date_fin_prevue)
                    emprunts.append(Emprunt(date_debut=date_debut, duree=duree, statut=Statut_Emprunt.en_cours, id_materiel=materiel.id_materiel, id_adherent=adherent.id_adherent, consommables_ids="[]"))
                    break
        for _ in range(36):
            for _tentative in range(200):
                materiel, adherent = rng.choice(materiels), rng.choice(adherents)
                duree, date_debut = rng.choice([1, 2]), aujourd_hui + timedelta(weeks=rng.choice([0, 1, 2, 3]))
                date_fin_prevue = date_debut + timedelta(weeks=duree)
                if disponible(materiel, date_debut, date_fin_prevue):
                    reserver(materiel, date_debut, date_fin_prevue)
                    emprunts.append(Emprunt(date_debut=date_debut, duree=duree, statut=Statut_Emprunt.reserve, id_materiel=materiel.id_materiel, id_adherent=adherent.id_adherent, consommables_ids="[]"))
                    break
        db.session.add_all(emprunts)
        db.session.commit()


if __name__ == "__main__":
    if "--confirm-reset" not in sys.argv:
        raise SystemExit("Cette commande remplace demo.db. Relancez avec --confirm-reset.")
    seed()
    print("Base de démonstration créée : instance/demo.db (120 matériels, 30 adhérents, 734 emprunts cohérents)")
    print("Pour lancer l'application avec cette base : définissez ASC_BRICOLAGE_DATABASE_URI=sqlite:///demo.db.")


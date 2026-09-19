"""Contrôles métier du jeu de démonstration généré."""

from datetime import date, timedelta

from models import Adherent, Emprunt, Materiel, Statut_Emprunt
from seed_demo import seed


def test_demo_seed_respects_rental_rules():
    seed()
    emprunts = Emprunt.query.all()
    assert Materiel.query.count() == 120
    assert Adherent.query.count() == 30
    assert len(emprunts) == 734
    assert all(emprunt.duree in (1, 2) for emprunt in emprunts)

    returned = [item for item in emprunts if item.statut == Statut_Emprunt.retourne]
    assert all(item.date_retour_effective is not None for item in returned)
    assert all((item.date_retour_effective - item.date_debut).days % 7 == 0 for item in returned)

    reservations = [item for item in emprunts if item.statut == Statut_Emprunt.reserve]
    assert all(date.today() <= item.date_debut <= date.today() + timedelta(weeks=3) for item in reservations)

    occupations = {}
    for item in emprunts:
        fin = item.date_retour_effective or item.date_debut + timedelta(weeks=item.duree)
        occupations.setdefault(item.id_materiel, []).append((item.date_debut, fin))
    for intervals in occupations.values():
        ordered = sorted(intervals)
        assert all(current[0] >= previous[1] for previous, current in zip(ordered, ordered[1:]))


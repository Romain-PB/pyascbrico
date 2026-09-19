# Tester l'application

Ce document décrit l'environnement de vérification local. Les tests utilisent
une base SQLite en mémoire : ils n'effacent jamais `site.db` ni `demo.db`.

## Première installation

Depuis le dossier du projet, installer les dépendances :

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

## Base de démonstration

Créer une base riche, sans toucher à la base normale :

```powershell
.\.venv\Scripts\python.exe seed_demo.py --confirm-reset
```

Lancer l'application sur cette base :

```powershell
$env:ASC_BRICOLAGE_DATABASE_URI = 'sqlite:///demo.db'
.\.venv\Scripts\python.exe app.py
```

Puis ouvrir `http://127.0.0.1:5000/stats`. Les tests automatisés utilisent une base SQLite en mémoire :

La base contient 120 matériels, 30 adhérents et 734 emprunts. Elle respecte
l'absence de chevauchement d'un même matériel, des locations prévues d'une ou
deux semaines, et des réservations au plus trois semaines à l'avance.

## Tests automatisés

Avant tout changement manuel, puis après celui-ci, exécuter :

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Un résultat `passed` indique que tous les scénarios attendus fonctionnent.
Pour exécuter une famille précise :

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_legacy_routes.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_stats.py -q
```

## Ce qui est protégé

| Fichier de tests | Rôle |
| --- | --- |
| `tests/test_legacy_routes.py` | Non-régression des pages historiques : accueil, matériels, adhérents, consommables, pannes, recettes et emprunts ; ajout d'un adhérent et d'un consommable ; absence de modification de données sur une consultation. |
| `tests/test_stats.py` | Constructeur de statistiques : locations, recettes, filtres de dates, catégories, moyens de paiement, validation des requêtes et rendu de pages. |
| `tests/test_demo_seed.py` | Jeu de démonstration : volume, absence de chevauchement, durées, retours hebdomadaires et limite des réservations. |
| `tests/conftest.py` | Jeu de données minimal isolé et réinitialisé automatiquement avant chaque test. |

## Règle de modification manuelle

1. Mettre à jour ou créer un test qui décrit le comportement souhaité.
2. Modifier le code.
3. Lancer toute la suite avec `pytest -q`.
4. Vérifier manuellement les écrans concernés avec `demo.db`.
5. Ne pas versionner `.venv`, `instance/*.db` ou les dossiers `__pycache__`.

Les tests ne remplacent pas une vérification visuelle, mais toute anomalie
trouvée manuellement doit idéalement devenir un test de non-régression.


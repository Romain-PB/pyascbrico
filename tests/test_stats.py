from stats_service import preview


def test_locations_grouped_by_material_counts_all_loans():
    result = preview({"source": "locations", "measure": "nombre_emprunts", "dimension": "materiel"})
    assert result["labels"] == ["Perceuse", "Tondeuse"]
    assert result["datasets"][0]["data"] == [2.0, 1.0]


def test_recettes_excludes_reservations():
    result = preview({"source": "recettes", "measure": "recettes_total", "dimension": None})
    assert result["datasets"][0]["data"] == [20.0]


def test_categories_use_business_labels():
    result = preview({"source": "locations", "measure": "nombre_emprunts", "dimension": "categorie"})
    assert result["labels"] == ["batiment", "jardinage"]


def test_locations_can_be_limited_to_a_period():
    result = preview({"source": "locations", "measure": "nombre_emprunts", "dimension": None, "filters": {"date_debut": "2026-01-01", "date_fin": "2026-01-31"}})
    assert result["datasets"][0]["data"] == [1.0]


def test_recettes_can_be_grouped_by_payment_type():
    result = preview({"source": "recettes", "measure": "recettes_total", "dimension": "type_paiement"})
    assert result["labels"] == ["CB"]
    assert result["datasets"][0]["data"] == [20.0]


def test_preview_endpoint_rejects_unknown_measure(client):
    response = client.post("/api/stats/preview", json={"source": "locations", "measure": "sql_libre"})
    assert response.status_code == 400


def test_stats_page_is_available(client):
    assert client.get("/stats").status_code == 200


def test_loans_page_renders_reservations(client):
    assert client.get("/emprunts").status_code == 200


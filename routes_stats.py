from flask import jsonify, render_template, request
from app import app
from models import Categorie, Etat, Statut_Emprunt, Type_Paiement
from stats_catalog import catalog_for_browser
from stats_service import StatisticsValidationError, preview


@app.route('/stats')
def stats():
    return render_template('stats.html', catalog=catalog_for_browser(), categories=[x.value for x in Categorie], etats=[x.value for x in Etat], statuts=[x.value for x in Statut_Emprunt], types_paiement=[x.value for x in Type_Paiement])


@app.route('/api/stats/preview', methods=['POST'])
def stats_preview():
    configuration = request.get_json(silent=True)
    if not isinstance(configuration, dict):
        return jsonify(error='La configuration JSON est requise.'), 400
    try:
        return jsonify(preview(configuration))
    except StatisticsValidationError as error:
        return jsonify(error=str(error)), 400


from flask import request, render_template
from app import app
from models import db, Materiel, Emprunt  # ajoute toutes tes tables ici

TABLES = {
    'Materiel': Materiel,
    'Emprunt': Emprunt,
}

@app.route('/explorateur', methods=['GET', 'POST'])
def explorer():
    selected_table = None
    filter_query = ""
    results = None
    columns = None
    error = None
    page = int(request.args.get('page', 1))
    per_page = 10  # lignes par page

    if request.method == 'POST':
        selected_table = request.form.get('table')
        filter_query = request.form.get('filter', '').strip()
        if selected_table in TABLES:
            model = TABLES[selected_table]
            try:
                query = db.session.query(model)
                if filter_query:
                    query = query.filter(db.text(filter_query))
                total_rows = query.count()
                results = query.offset((page-1)*per_page).limit(per_page).all()
                columns = model.__table__.columns.keys()
            except Exception as e:
                error = str(e)
        else:
            error = "Table invalide."

    return render_template('explorer.html',
                           tables=TABLES.keys(),
                           selected_table=selected_table,
                           filter_query=filter_query,
                           results=results,
                           columns=columns,
                           error=error,
                           page=page,
                           per_page=per_page)

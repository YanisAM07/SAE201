import csv
import io
from flask import Blueprint, render_template, request, Response
from models.db import Session
from models.dimensions import ProfessionSante, Departement
from services.ameli_api import AmeliAPI

bp_effectifs = Blueprint("effectifs", __name__)

api = AmeliAPI()

@bp_effectifs.route("/effectifs")
def afficher():
    """Affiche les effectifs pour la sélection de l'utilisateur."""
    profession_id = request.args.get("profession_id", type=int)
    departement_id = request.args.get("departement_id", type=int)
    annee = request.args.get("annee", type=int)

    session = Session()
    try:
        prof = session.get(ProfessionSante, profession_id)
        dept = session.get(Departement, departement_id)
        if not prof or not dept or not annee:
            return render_template(
                "erreur.html",
                message="Paramètres manquants."
            ), 400

        resultats = api.get_effectifs(prof.libelle, dept.code, annee)
        evolution = api.get_evolution_effectifs(prof.libelle, dept.code)

        return render_template(
            "effectifs.html",
            prof=prof,
            dept=dept,
            annee=annee,
            resultats=resultats,
            evolution=evolution
        )
    finally:
        session.close()

@bp_effectifs.route("/export/csv")
def export_csv():
    """Exporte l'évolution des effectifs au format CSV."""
    profession_id = request.args.get("profession_id", type=int)
    departement_id = request.args.get("departement_id", type=int)

    session = Session()
    try:
        prof = session.get(ProfessionSante, profession_id)
        dept = session.get(Departement, departement_id)

        if not prof or not dept:
            return "Paramètres manquants", 400

        # Récupération des données d'évolution pour toutes les années
        evolution = api.get_evolution_effectifs(prof.libelle, dept.code)

        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')

        # En-têtes du fichier
        writer.writerow(['Année', 'Effectif', 'Densité'])

        # Remplissage avec les données
        for row in evolution:
            writer.writerow([row.get('annee'), row.get('effectif'), row.get('densite')])

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename=effectifs_{dept.code}_{prof.libelle}.csv"}
        )
    finally:
        session.close()
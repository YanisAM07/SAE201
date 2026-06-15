from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import ProfessionSante, Region
# Assure-toi que AmeliAPI est bien importé depuis ton fichier services/ameli_api.py

bp_honoraires = Blueprint("honoraires", __name__)

@bp_honoraires.route("/honoraires")
def index():
    session = Session()
    try:
        professions = session.query(ProfessionSante).order_by(ProfessionSante.libelle).all()
        regions = session.query(Region).order_by(Region.libelle).all()
        
        # Le reste de ta logique de récupération de résultats
        return render_template("honoraires.html", professions=professions, regions=regions)
    finally:
        session.close()
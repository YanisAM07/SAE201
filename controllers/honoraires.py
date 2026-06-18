from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import ProfessionSante, Region, Departement
from services.ameli_api import AmeliAPI 

bp_honoraires = Blueprint("honoraires", __name__)
api = AmeliAPI()

@bp_honoraires.route("/honoraires")
def index():
    session = Session()
    try:
        professions = session.query(ProfessionSante).order_by(ProfessionSante.libelle).all()
        regions = session.query(Region).order_by(Region.libelle).all()
        
        prof_id = request.args.get("profession_id", type=int)
        dept_id = request.args.get("departement_id", type=int)
        
        resultats = []
        
        if prof_id and dept_id:
            profession = session.query(ProfessionSante).get(prof_id)
            departement = session.query(Departement).get(dept_id)
            
            if profession and departement:
                resultats = api.get_honoraires(profession.libelle, departement.code)

        return render_template("honoraires.html", professions=professions, regions=regions, resultats=resultats)
    finally:
        session.close()
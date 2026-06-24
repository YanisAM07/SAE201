from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import ProfessionSante, Region, Departement
from services.ameli_api import AmeliAPI

bp_demographie = Blueprint("demographie", __name__)
api = AmeliAPI()

@bp_demographie.route("/demographie")
def index():
    session = Session()
    try:
        # Données pour remplir le formulaire en cascade
        professions = session.query(ProfessionSante).order_by(ProfessionSante.libelle).all()
        regions = session.query(Region).order_by(Region.libelle).all()
        
        prof_id = request.args.get("profession_id", type=int)
        dept_id = request.args.get("departement_id", type=int)
        annee = request.args.get("annee", type=int, default=2023)
        
        profil = None
        profession_selectionnee = None
        departement_selectionne = None
        
        if prof_id and dept_id:
            profession_selectionnee = session.query(ProfessionSante).get(prof_id)
            departement_selectionne = session.query(Departement).get(dept_id)
            
            if profession_selectionnee and departement_selectionne:
                # Récupération du profil démographique trié par notre méthode
                profil = api.get_profil_demographique(
                    profession_selectionnee.libelle, 
                    departement_selectionne.code, 
                    annee
                )

        return render_template(
            "demographie.html",
            professions=professions,
            regions=regions,
            profil=profil,
            profession_selectionnee=profession_selectionnee,
            departement_selectionne=departement_selectionne,
            annee_selectionnee=annee
        )
    finally:
        session.close()
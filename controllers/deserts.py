from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import ProfessionSante
from services.ameli_api import AmeliAPI

bp_deserts = Blueprint("deserts", __name__)
api = AmeliAPI()

@bp_deserts.route("/deserts")
def index():
    session = Session()
    try:
        # Récupération de la liste des professions pour le menu déroulant
        professions = session.query(ProfessionSante).order_by(ProfessionSante.libelle).all()
        
        prof_id = request.args.get("profession_id", type=int)
        annee = request.args.get("annee", type=int, default=2023)
        
        resultats = []
        top_5 = []
        flop_5 = []
        moyenne_nationale = 0
        profession_selectionnee = None
        
        if prof_id and annee:
            profession_selectionnee = session.query(ProfessionSante).get(prof_id)
            if profession_selectionnee:
                # Appel à notre nouvelle méthode d'API
                resultats = api.get_national_densites(profession_selectionnee.libelle, annee)
                
                if resultats:
                    # Calcul de la moyenne nationale de densité
                    total_densite = sum(float(r.get('densite', 0) or 0) for r in resultats)
                    moyenne_nationale = round(total_densite / len(resultats), 2)
                    
                    # Extraction Top 5 (les 5 premiers éléments)
                    top_5 = resultats[:5]
                    
                    # Extraction Flop 5 (les 5 derniers éléments inversés pour afficher le pire en premier)
                    flop_5 = list(reversed(resultats[-5:]))

        return render_template(
            "deserts.html",
            professions=professions,
            resultats=resultats,
            top_5=top_5,
            flop_5=flop_5,
            moyenne_nationale=moyenne_nationale,
            profession_selectionnee=profession_selectionnee,
            annee_selectionnee=annee
        )
    finally:
        session.close()
from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import ProfessionSante, Region, Departement
from services.ameli_api import AmeliAPI

bp_deserts = Blueprint("deserts", __name__)
api = AmeliAPI()

@bp_deserts.route("/deserts")
def index():
    session = Session()
    try:
        professions = session.query(ProfessionSante).order_by(ProfessionSante.libelle).all()
        regions = session.query(Region).order_by(Region.libelle).all()

        prof_id = request.args.get("profession_id", type=int)
        annee = request.args.get("annee", type=int, default=2023)
        region_id = request.args.get("region_id", type=int)

        resultats = []
        top_5 = []
        flop_5 = []
        moyenne_nationale = 0
        profession_selectionnee = None
        region_selectionnee = None
        codes_departements_region = []

        if region_id:
            region_selectionnee = session.get(Region, region_id)
            if region_selectionnee:
                codes_departements_region = [
                    d.code for d in session.query(Departement)
                    .filter_by(region_id=region_id).all()
                ]

        if prof_id and annee:
            profession_selectionnee = session.get(ProfessionSante, prof_id)
            if profession_selectionnee:
                # Appel à notre méthode d'API
                resultats = api.get_national_densites(profession_selectionnee.libelle, annee)

                # Filtre par région si demandé : on ne garde que les départements de la région
                if region_id and codes_departements_region:
                    codes_norm = [c.zfill(2) for c in codes_departements_region]
                    resultats = [
                        r for r in resultats
                        if str(r.get("departement")).strip().zfill(2) in codes_norm
                    ]

                if resultats:
                    # Calcul de la moyenne nationale (ou régionale si filtre actif) de densité
                    total_densite = sum(float(r.get('densite', 0) or 0) for r in resultats)
                    moyenne_nationale = round(total_densite / len(resultats), 2)

                    # Extraction Top 5 / Flop 5 (le tri par densité DESC est déjà fait par l'API)
                    top_5 = resultats[:5]
                    flop_5 = list(reversed(resultats[-5:]))

        return render_template(
            "deserts.html",
            professions=professions,
            regions=regions,
            resultats=resultats,
            top_5=top_5,
            flop_5=flop_5,
            moyenne_nationale=moyenne_nationale,
            profession_selectionnee=profession_selectionnee,
            annee_selectionnee=annee,
            region_selectionnee=region_selectionnee,
            codes_departements_region=codes_departements_region
        )
    finally:
        session.close()
from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import Region, Departement
from services.ameli_api import AmeliAPI

bp_pathologies = Blueprint("pathologies", __name__)
api = AmeliAPI()

@bp_pathologies.route("/pathologies")
def index():
    session = Session()
    try:
        regions = session.query(Region).order_by(Region.libelle).all()
        categories = api.CATEGORIES_PATHOLOGIES

        patho = request.args.get("patho", type=str)
        annee = request.args.get("annee", type=int, default=2023)
        region_id = request.args.get("region_id", type=int)

        resultats = []
        top_5 = []
        flop_5 = []
        region_selectionnee = None
        codes_departements_region = []

        if region_id:
            region_selectionnee = session.get(Region, region_id)
            if region_selectionnee:
                codes_departements_region = [
                    d.code for d in session.query(Departement)
                    .filter_by(region_id=region_id).all()
                ]

        if patho and annee:
            resultats = api.get_pathologie_national(patho, annee)

            # On trie par prévalence décroissante si l'info est disponible,
            # sinon on garde l'ordre retourné par l'API.
            try:
                resultats = sorted(
                    resultats,
                    key=lambda r: float(r.get("prevalence") or 0),
                    reverse=True
                )
            except (TypeError, ValueError):
                pass

            # Filtre par région si demandé : on ne garde que les départements de la région
            if region_id and codes_departements_region:
                codes_norm = [c.zfill(2) for c in codes_departements_region]
                resultats = [
                    r for r in resultats
                    if str(r.get("departement")).strip().zfill(2) in codes_norm
                ]

            if resultats:
                top_5 = resultats[:5]
                flop_5 = list(reversed(resultats[-5:]))

        return render_template(
            "pathologies.html",
            regions=regions,
            categories=categories,
            resultats=resultats,
            top_5=top_5,
            flop_5=flop_5,
            patho_selectionnee=patho,
            annee_selectionnee=annee,
            region_selectionnee=region_selectionnee,
            codes_departements_region=codes_departements_region
        )
    finally:
        session.close()
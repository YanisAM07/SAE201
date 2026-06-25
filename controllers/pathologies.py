from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import Region, Departement
from services.ameli_api import AmeliAPI

# Initialisation du blueprint pour la page des pathologies
bp_pathologies = Blueprint("pathologies", __name__)
# Instanciation du service pour l'API Ameli
api = AmeliAPI()

@bp_pathologies.route("/pathologies")
def index():
    """Route d'affichage et de traitement pour la page des pathologies."""
    # Ouverture de la session de base de données
    session = Session()
    try:
        # Récupération des régions et des catégories de pathologies disponibles
        regions = session.query(Region).order_by(Region.libelle).all()
        categories = api.CATEGORIES_PATHOLOGIES

        # Récupération des paramètres envoyés via l'URL (méthode GET)
        patho = request.args.get("patho", type=str)
        annee = request.args.get("annee", type=int, default=2023)
        region_id = request.args.get("region_id", type=int)

        # Initialisation des variables pour le template
        resultats = []
        top_5 = []
        flop_5 = []
        region_selectionnee = None
        codes_departements_region = []

        # Si une région est sélectionnée, on récupère ses informations et ses départements associés
        if region_id:
            region_selectionnee = session.get(Region, region_id)
            if region_selectionnee:
                codes_departements_region = [
                    d.code for d in session.query(Departement)
                    .filter_by(region_id=region_id).all()
                ]

        # Si les paramètres obligatoires sont présents, on lance la recherche
        if patho and annee:
            resultats = api.get_pathologie_national(patho, annee)

            # Tentative de tri des résultats par prévalence décroissante
            # Si la donnée n'est pas disponible ou invalide, on conserve l'ordre de l'API
            try:
                resultats = sorted(
                    resultats,
                    key=lambda r: float(r.get("prevalence") or 0),
                    reverse=True
                )
            except (TypeError, ValueError):
                pass

            # Filtrage des résultats pour ne conserver que les départements de la région sélectionnée
            if region_id and codes_departements_region:
                codes_norm = [c.zfill(2) for c in codes_departements_region]
                resultats = [
                    r for r in resultats
                    if str(r.get("departement")).strip().zfill(2) in codes_norm
                ]

            # Extraction des 5 départements les plus touchés et des 5 les moins touchés
            if resultats:
                top_5 = resultats[:5]
                flop_5 = list(reversed(resultats[-5:]))

        # Envoi de l'ensemble des données préparées au template HTML
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
        # Fermeture de la session de base de données
        session.close()
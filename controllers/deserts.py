from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import ProfessionSante, Region, Departement
from services.ameli_api import AmeliAPI

# Initialisation du blueprint pour la page des déserts médicaux
bp_deserts = Blueprint("deserts", __name__)
api = AmeliAPI()

@bp_deserts.route("/deserts")
def index():
    """Route d'affichage et de calcul pour la page des déserts médicaux."""
    # Ouverture de la session de base de données
    session = Session()
    try:
        # Récupération des données nécessaires pour les listes déroulantes du formulaire
        professions = session.query(ProfessionSante).order_by(ProfessionSante.libelle).all()
        regions = session.query(Region).order_by(Region.libelle).all()

        # Lecture des paramètres passés en GET dans l'URL
        prof_id = request.args.get("profession_id", type=int)
        annee = request.args.get("annee", type=int, default=2023)
        region_id = request.args.get("region_id", type=int)

        # Initialisation des variables par défaut pour le template
        resultats = []
        top_5 = []
        flop_5 = []
        moyenne_nationale = 0
        profession_selectionnee = None
        region_selectionnee = None
        codes_departements_region = []

        # Traitement du filtre régional s'il est renseigné
        if region_id:
            region_selectionnee = session.get(Region, region_id)
            if region_selectionnee:
                # Extraction des codes des départements appartenant à cette région
                codes_departements_region = [
                    d.code for d in session.query(Departement)
                    .filter_by(region_id=region_id).all()
                ]

        # Lancement de la recherche si les paramètres obligatoires sont présents
        if prof_id and annee:
            profession_selectionnee = session.get(ProfessionSante, prof_id)
            if profession_selectionnee:
                # Appel à l'API pour récupérer les densités à l'échelle nationale
                resultats = api.get_national_densites(profession_selectionnee.libelle, annee)

                # Filtrage local des résultats pour ne conserver que la région ciblée
                if region_id and codes_departements_region:
                    codes_norm = [c.zfill(2) for c in codes_departements_region]
                    resultats = [
                        r for r in resultats
                        if str(r.get("departement")).strip().zfill(2) in codes_norm
                    ]

                # Calcul des statistiques si la liste de résultats n'est pas vide
                if resultats:
                    # Calcul de la moyenne nationale (ou régionale selon le filtre)
                    total_densite = sum(float(r.get('densite', 0) or 0) for r in resultats)
                    moyenne_nationale = round(total_densite / len(resultats), 2)

                    # Extraction du Top 5 et Flop 5 (les données API sont déjà triées par densité DESC)
                    top_5 = resultats[:5]
                    flop_5 = list(reversed(resultats[-5:]))

        # Envoi de toutes les données préparées au template
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
        # Fermeture de la session
        session.close()
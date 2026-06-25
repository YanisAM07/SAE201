from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import ProfessionSante, Departement, Region
from services.ameli_api import AmeliAPI

# Initialisation du blueprint et de l'instance de l'API
bp_comparaison = Blueprint("comparaison", __name__)
api = AmeliAPI()


def _charger_cote(session, prefixe):
    """
    Charge les données d'un "côté" du comparatif (A ou B) à partir des
    paramètres de requête préfixés (ex: profession_a_id, departement_a_id).
    Retourne un dict avec prof, dept, resultats, evolution (ou None si
    la sélection est incomplète).
    """
    # Récupération des identifiants dans l'URL
    prof_id = request.args.get(f"profession_{prefixe}_id", type=int)
    dept_id = request.args.get(f"departement_{prefixe}_id", type=int)

    # Arrêt si un paramètre est manquant
    if not prof_id or not dept_id:
        return None

    # Recherche des entités en base de données
    prof = session.get(ProfessionSante, prof_id)
    dept = session.get(Departement, dept_id)

    # Arrêt si la profession ou le département n'existe pas
    if not prof or not dept:
        return None

    # Appel à l'API pour obtenir l'historique
    evolution = api.get_evolution_effectifs(prof.libelle, dept.code)

    return {
        "prof": prof,
        "dept": dept,
        "evolution": evolution,
    }


@bp_comparaison.route("/comparaison")
def index():
    # Ouverture de la session de base de données
    session = Session()
    try:
        # Récupération de toutes les options pour les menus déroulants
        professions = session.query(ProfessionSante).order_by(ProfessionSante.libelle).all()
        regions = session.query(Region).order_by(Region.libelle).all()
        departements = session.query(Departement).order_by(Departement.code).all()

        # Chargement des données sélectionnées par l'utilisateur (côté A et B)
        cote_a = _charger_cote(session, "a")
        cote_b = _charger_cote(session, "b")

        # Rendu du template avec l'ensemble des variables
        return render_template(
            "comparaison.html",
            professions=professions,
            regions=regions,
            departements=departements,
            cote_a=cote_a,
            cote_b=cote_b,
            BASE_URL="",
        )
    finally:
        # Fermeture de la session pour libérer la connexion
        session.close()
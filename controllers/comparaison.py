from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import ProfessionSante, Departement, Region
from services.ameli_api import AmeliAPI

bp_comparaison = Blueprint("comparaison", __name__)
api = AmeliAPI()


def _charger_cote(session, prefixe):
    """
    Charge les données d'un "côté" du comparatif (A ou B) à partir des
    paramètres de requête préfixés (ex: profession_a_id, departement_a_id).
    Retourne un dict avec prof, dept, resultats, evolution (ou None si
    la sélection est incomplète).
    """
    prof_id = request.args.get(f"profession_{prefixe}_id", type=int)
    dept_id = request.args.get(f"departement_{prefixe}_id", type=int)

    if not prof_id or not dept_id:
        return None

    prof = session.get(ProfessionSante, prof_id)
    dept = session.get(Departement, dept_id)

    if not prof or not dept:
        return None

    evolution = api.get_evolution_effectifs(prof.libelle, dept.code)

    return {
        "prof": prof,
        "dept": dept,
        "evolution": evolution,
    }


@bp_comparaison.route("/comparaison")
def index():
    session = Session()
    try:
        professions = session.query(ProfessionSante).order_by(ProfessionSante.libelle).all()
        regions = session.query(Region).order_by(Region.libelle).all()
        departements = session.query(Departement).order_by(Departement.code).all()

        cote_a = _charger_cote(session, "a")
        cote_b = _charger_cote(session, "b")

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
        session.close()
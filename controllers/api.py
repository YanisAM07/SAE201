from flask import Blueprint, jsonify
from models.db import Session
from models.dimensions import Departement

# Définition du blueprint pour l'API avec le préfixe /api
bp_api = Blueprint("api", __name__, url_prefix="/api")

@bp_api.route("/departements/<int:region_id>")
def departements(region_id):
    """Retourne les départements d'une région au format JSON."""
    # Ouverture de la session de base de données
    session = Session()
    try:
        # Récupération des départements filtrés par région et triés par code
        depts = (
            session.query(Departement)
            .filter_by(region_id=region_id)
            .order_by(Departement.code)
            .all()
        )
        
        # Construction manuelle de la liste des dictionnaires pour la sérialisation
        liste_depts = []
        for d in depts:
            liste_depts.append({
                "id": d.id,
                "code": d.code,
                "libelle": d.libelle
            })
            
        # Renvoi des données au format JSON
        return jsonify(liste_depts)
    finally:
        # Fermeture de la session
        session.close()
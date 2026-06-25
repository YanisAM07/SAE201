from flask import Blueprint, render_template
from models.db import Session
from models.dimensions import Region, ProfessionSante, Departement, Annee

# Initialisation du blueprint pour la page d'accueil
bp_accueil = Blueprint("accueil", __name__)


@bp_accueil.route("/acceuil")
def index():
    """Route principale pour l'affichage de la page d'accueil."""
    # Ouverture d'une nouvelle session de base de données
    session = Session()
    try:
        # Récupération des données nécessaires pour les menus déroulants
        regions = session.query(Region).order_by(Region.libelle).all()
        professions = (session.query(ProfessionSante).order_by(ProfessionSante.libelle).all())
        departements = session.query(Departement).order_by(Departement.code).all()

        # Envoi des listes au template HTML pour affichage
        return render_template(
            "accueil.html",
            regions=regions,
            professions=professions,
            departements=departements,
            BASE_URL=""
        )
    finally:
        # Fermeture systématique de la session après exécution
        session.close()
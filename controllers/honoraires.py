from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import ProfessionSante, Region, Departement
from services.ameli_api import AmeliAPI 

# Initialisation du blueprint pour la gestion des honoraires
bp_honoraires = Blueprint("honoraires", __name__)
# Instanciation du service pour communiquer avec l'API
api = AmeliAPI()

@bp_honoraires.route("/honoraires")
def index():
    """Route principale pour l'affichage des données d'honoraires."""
    # Ouverture de la session de base de données
    session = Session()
    try:
        # Récupération des listes pour alimenter les menus déroulants
        professions = session.query(ProfessionSante).order_by(ProfessionSante.libelle).all()
        regions = session.query(Region).order_by(Region.libelle).all()
        
        # Lecture des identifiants passés en paramètres d'URL (GET)
        prof_id = request.args.get("profession_id", type=int)
        dept_id = request.args.get("departement_id", type=int)
        
        # Initialisation du tableau de résultats par défaut
        resultats = []
        
        # Si le formulaire a été soumis avec les deux paramètres
        if prof_id and dept_id:
            # Recherche des entités en base de données
            profession = session.query(ProfessionSante).get(prof_id)
            departement = session.query(Departement).get(dept_id)
            
            # Vérification que la profession et le département existent bien
            if profession and departement:
                # Appel à l'API pour récupérer l'historique des honoraires
                resultats = api.get_honoraires(profession.libelle, departement.code)

        # Envoi des données préparées au template HTML
        return render_template("honoraires.html", professions=professions, regions=regions, resultats=resultats)
    finally:
        # Fermeture systématique de la session
        session.close()
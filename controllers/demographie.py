from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import ProfessionSante, Region, Departement
from services.ameli_api import AmeliAPI

# Initialisation du blueprint et instanciation de l'API
bp_demographie = Blueprint("demographie", __name__)
api = AmeliAPI()

@bp_demographie.route("/demographie")
def index():
    """Affiche la page des profils démographiques selon l'âge et le sexe."""
    # Ouverture de la session de base de données
    session = Session()
    try:
        # Récupération des données pour remplir le formulaire en cascade
        professions = session.query(ProfessionSante).order_by(ProfessionSante.libelle).all()
        regions = session.query(Region).order_by(Region.libelle).all()
        
        # Récupération des paramètres de la requête URL (GET)
        prof_id = request.args.get("profession_id", type=int)
        dept_id = request.args.get("departement_id", type=int)
        annee = request.args.get("annee", type=int, default=2023)
        
        # Initialisation des variables de résultats
        profil = None
        profession_selectionnee = None
        departement_selectionne = None
        
        # Traitement si l'utilisateur a soumis le formulaire avec une profession et un département
        if prof_id and dept_id:
            # Recherche des entités correspondantes en base de données
            profession_selectionnee = session.query(ProfessionSante).get(prof_id)
            departement_selectionne = session.query(Departement).get(dept_id)
            
            # Si les deux entités existent, on lance la requête
            if profession_selectionnee and departement_selectionne:
                # Récupération du profil démographique trié par notre méthode via l'API
                profil = api.get_profil_demographique(
                    profession_selectionnee.libelle, 
                    departement_selectionne.code, 
                    annee
                )

        # Génération du rendu HTML avec passage de l'ensemble des variables
        return render_template(
            "demographie.html",
            professions=professions,
            regions=regions,
            profil=profil,
            profession_selectionnee=profession_selectionnee,
            departement_selectionne=departement_selectionne,
            annee_selectionnee=annee
        )
    finally:
        # Fermeture de la session pour libérer les ressources
        session.close()
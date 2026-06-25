import csv
import io
from flask import Blueprint, render_template, request, Response
from models.db import Session
from models.dimensions import ProfessionSante, Departement
from services.ameli_api import AmeliAPI

# Initialisation du blueprint pour la gestion des effectifs
bp_effectifs = Blueprint("effectifs", __name__)

# Instanciation du service API Ameli
api = AmeliAPI()

@bp_effectifs.route("/effectifs")
def afficher():
    """Route principale pour l'affichage des effectifs selon la sélection de l'utilisateur."""
    # Récupération des paramètres de l'URL
    profession_id = request.args.get("profession_id", type=int)
    departement_id = request.args.get("departement_id", type=int)
    annee = request.args.get("annee", type=int)

    # Ouverture de la session de base de données
    session = Session()
    try:
        # Recherche des entités en base
        prof = session.get(ProfessionSante, profession_id)
        dept = session.get(Departement, departement_id)
        
        # Vérification de la présence de tous les paramètres requis
        if not prof or not dept or not annee:
            return render_template(
                "erreur.html",
                message="Paramètres manquants."
            ), 400

        # Récupération des données ponctuelles et de l'évolution via l'API
        resultats = api.get_effectifs(prof.libelle, dept.code, annee)
        evolution = api.get_evolution_effectifs(prof.libelle, dept.code)

        # Rendu du template avec les données récupérées
        return render_template(
            "effectifs.html",
            prof=prof,
            dept=dept,
            annee=annee,
            resultats=resultats,
            evolution=evolution
        )
    finally:
        # Fermeture de la session
        session.close()

@bp_effectifs.route("/export/csv")
def export_csv():
    """Route pour l'export de l'évolution des effectifs au format CSV."""
    # Récupération des paramètres nécessaires pour l'export
    profession_id = request.args.get("profession_id", type=int)
    departement_id = request.args.get("departement_id", type=int)

    # Ouverture de la session de base de données
    session = Session()
    try:
        # Recherche des entités en base
        prof = session.get(ProfessionSante, profession_id)
        dept = session.get(Departement, departement_id)

        # Vérification de la validité des paramètres
        if not prof or not dept:
            return "Paramètres manquants", 400

        # Récupération de l'historique complet pour la génération du fichier
        evolution = api.get_evolution_effectifs(prof.libelle, dept.code)

        # Création d'un buffer en mémoire pour écrire le CSV
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')

        # Écriture de la ligne d'en-tête
        writer.writerow(['Année', 'Effectif', 'Densité'])

        # Parcours des données et écriture ligne par ligne
        for row in evolution:
            writer.writerow([row.get('annee'), row.get('effectif'), row.get('densite')])

        # Construction et renvoi de la réponse HTTP avec les headers pour forcer le téléchargement
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename=effectifs_{dept.code}_{prof.libelle}.csv"}
        )
    finally:
        # Fermeture de la session
        session.close()
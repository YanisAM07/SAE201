from flask import Blueprint, render_template

# Initialisation du blueprint pour la page de présentation
bp_presentation = Blueprint("presentation", __name__)

@bp_presentation.route("/")
def index():
    """Route de base qui affiche la page de présentation principale."""
    # Rendu du template HTML correspondant
    return render_template("presentation.html")
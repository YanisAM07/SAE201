from flask import Blueprint, render_template

bp_presentation = Blueprint("presentation", __name__)

@bp_presentation.route("/")
def index():
    return render_template("presentation.html")
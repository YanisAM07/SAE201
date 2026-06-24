import os
from flask import Flask, render_template
from config import Config
from controllers.accueil import bp_accueil
from controllers.api import bp_api
from controllers.effectifs import bp_effectifs
from controllers.honoraires import bp_honoraires
from controllers.deserts import bp_deserts
from controllers.demographie import bp_demographie
from controllers.presentation import bp_presentation


app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(bp_api)
app.register_blueprint(bp_accueil)
app.register_blueprint(bp_effectifs)
app.register_blueprint(bp_honoraires)
app.register_blueprint(bp_deserts)
app.register_blueprint(bp_demographie)
app.register_blueprint(bp_presentation)

app.config['BASE_URL'] = os.getenv('APP_BASE_URL', '')

@app.context_processor
def inject_base_url():
    return {"BASE_URL": app.config["BASE_URL"]}

@app.errorhandler(404)
def page_non_trouvee(e):
    return render_template("erreur.html", message="Page non trouvée."), 404

if __name__ == "__main__":
    app.run(debug=True)
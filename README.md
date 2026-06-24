# SAE 201  : Application Web et Visualisation de Données (Open Data)

Ce projet consiste en la création d'une application web dynamique complète permettant de visualiser et d'analyser des données complexes de santé. Il est réalisé en synergie directe avec la **SAE 204** (exploitation de la base de données) et la **SAE 205** (gestion de projet).

L'objectif principal est de concevoir un outil d'aide à la décision à destination d'utilisateurs cibles, en s'appuyant sur les données Open Data de l'Assurance Maladie (ameli.fr) concernant les effectifs, honoraires et prescriptions.

##  Liens Inter-SAE
* **SAE 201 (Développement Web) :** Réalisation du site en Python (framework Flask), architecture MVC, gestion des routes, des formulaires et intégration des vues (HTML/CSS/JS).
* **SAE 204 (Base de données) :** Conception, requêtage et structuration de la base de données MySQL qui alimente dynamiquement l'application web.
* **SAE 205 (Gestion de projet) :** Suivi du cahier des charges, planification des livrables, répartition des tâches et démarche qualité (Git/GitHub).

##  Stack Technique & Architecture

### Backend & Données
* **Flask 3 :** Framework web Python principal utilisant les Blueprints pour séparer les fonctionnalités.
* **SQLAlchemy :** ORM réutilisé depuis la SAE 204 pour requêter la base de données MySQL (composée de 9 tables de dimensions).
* **Données Open Data :** Intégration et requêtage des jeux de données d'ameli.fr.

### Frontend & Visualisation
* **Jinja2 :** Moteur de templates HTML avec système d'héritage, filtres et boucles.
* **CSS & Bootstrap :** Mise en forme graphique, design simple et responsive.
* **JavaScript (Fetch / AJAX) :** Gestion des requêtes asynchrones en cascade pour mettre à jour les données et les graphiques sans recharger la page.
* **Chart.js :** Génération de 4 types de graphiques interactifs (courbes, camemberts, multi-axes, etc.) pour la comparaison de données.

### Structure du Code (Modèle-Vue-Contrôleur)
* `/controllers` : Gestion de la logique des routes
* `/models` : Représentation, accès et manipulation des données via l'ORM.
* `/services` : Logique métier, calculs intermédiaires et traitements de données.
* `/templates` : Pages HTML dynamiques héritées.
* `/static` : Ressources statiques (CSS personnalisé, scripts JS, médias).

##  Installation et Lancement local

### 1. Cloner le dépôt
git clone https://github.com/YanisAM07/SAE201.git
cd SAE201

### 2. Configurer l'environnement virtuel et installer les dépendances
Il est recommandé d'utiliser un environnement virtuel :
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

Installation des packages requis :
pip install -r requirements.txt

### 3. Fichier de configuration locale
Dupliquer le fichier d'exemple pour configurer les variables d'environnement locales (accès BDD MySQL Alwaysdata, clés secrètes) :
cp .env.exemple .env

### 4. Exécuter l'application
python app.py

L'application est accessible localement à l'adresse : http://127.0.0.1:5000

##  Équipe de développement
* **Gurbuz Semih**
* **Grosjean--Notardonato Louka**
* **Ait-Meziane Yanis**
* **Silva Dos Santos Gustavo**
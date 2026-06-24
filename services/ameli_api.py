import requests

class AmeliAPI:
    """Service d'accès à l'API data.ameli.fr."""

    BASE_URL = "https://data.ameli.fr/api/explore/v2.1/catalog/datasets"

    def __init__(self, timeout=10):
        self._timeout = timeout
        self._session = requests.Session()

    def get_effectifs(self, profession, departement_code, annee):
        """
        Effectifs pour une profession, un département et une année.
        Retourne une liste de dictionnaires {annee, effectif, densite}.
        """
        where = (
            f"profession_sante=\"{profession}\" AND "
            f"departement=\"{departement_code}\" AND "
            f"year(annee)={annee} AND "
            f"libelle_classe_age=\"Tout âge\" AND "
            f"libelle_sexe=\"tout sexe\""
        )

        return self._requete(
            "demographie-effectifs-et-les-densites",
            {"select": "annee,effectif,densite", "where": where, "limit": 100},
        )

    def get_evolution_effectifs(self, profession, departement_code):
        """Effectifs sur toutes les années disponibles (pour un graphique)."""
        where = (
            f"profession_sante=\"{profession}\" AND "
            f"departement=\"{departement_code}\" AND "
            f"libelle_classe_age=\"Tout âge\" AND "
            f"libelle_sexe=\"tout sexe\""
        )

        return self._requete(
            "demographie-effectifs-et-les-densites",
            {
                "select": "annee,effectif,densite",
                "where": where,
                "order_by": "annee",
                "limit": 100,
            },
        )

    def _requete(self, dataset, params):
        """Méthode privée : effectue une requête GET et gère les erreurs."""
        url = f"{self.BASE_URL}/{dataset}/records"
        try:
            resp = self._session.get(url, params=params, timeout=self._timeout)
            resp.raise_for_status()
            return resp.json().get("results", [])
        except requests.RequestException as e:
            print(f"[AmeliAPI] Erreur lors de la requête : {e}")
            return []
    
    def get_honoraires(self, profession, departement_code):
        """
        Récupère les données d'honoraires pour une profession et un département.
        """
        dataset = "honoraires" 
        where = (
            f"profession_sante=\"{profession}\" AND "
            f"departement=\"{departement_code}\""
        )

        return self._requete(
            dataset,
            {
                "where": where, 
                "order_by": "annee DESC", 
                "limit": 100
            },
        )
    
    def get_national_densites(self, profession, annee):
        """
        Récupère la densité médicale des départements pour une profession et une année données.
        """
        dataset = "demographie-effectifs-et-les-densites"
        
        # Le retour à TA formule d'origine qui marchait parfaitement !
        where = (
            f"profession_sante=\"{profession}\" AND "
            f"year(annee)={annee} AND "
            f"libelle_classe_age=\"Tout âge\" AND "
            f"libelle_sexe=\"tout sexe\""
        )

        resultats_bruts = self._requete(
            dataset,
            {
                "where": where,
                "order_by": "densite DESC",
                "limit": 100  # On garde absolument ça pour ne pas faire planter l'API
            },
        )
        
        # On filtre la France entière en Python
        resultats_propres = [r for r in resultats_bruts if str(r.get("departement")) != "999"]
        
        return resultats_propres
    
    def get_profil_demographique(self, profession, departement_code, annee):
        """
        Récupère l'ensemble des données démographiques (tranches d'âge et sexes)
        pour une profession, un département et une année spécifiques.
        """
        dataset = "demographie-effectifs-et-les-densites"
        
        # On cible la profession, le département et l'année demandée
        where = (
            f"profession_sante=\"{profession}\" AND "
            f"departement=\"{departement_code}\" AND "
            f"year(annee)={annee}"
        )

        # On récupère l'ensemble des lignes correspondantes
        resultats_bruts = self._requete(
            dataset,
            {
                "where": where,
                "limit": 100
            },
        )

        # On organise le tri en Python pour alimenter nos futurs graphiques Chart.js
        donnees_sexe = []
        donnees_age = []

        for r in resultats_bruts:
            lib_age = r.get("libelle_classe_age", "Tout âge")
            lib_sexe = r.get("libelle_sexe", "tout sexe")
            
            # 1. Filtre pour la mixité (On veut l'âge global découpé par sexe)
            if lib_age == "Tout âge" and lib_sexe != "tout sexe":
                donnees_sexe.append({
                    "sexe": lib_sexe,
                    "effectif": r.get("effectif", 0)
                })
                
            # 2. Filtre pour le vieillissement (On veut le sexe global découpé par tranches d'âge)
            elif lib_sexe == "tout sexe" and lib_age != "Tout âge":
                donnees_age.append({
                    "classe_age": lib_age,
                    "effectif": r.get("effectif", 0)
                })

        return {
            "repartition_sexe": donnees_sexe,
            "repartition_age": donnees_age
        }
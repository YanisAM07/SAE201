import requests

class AmeliAPI:
    """Service d'accès à l'API data.ameli.fr."""

    BASE_URL = "https://data.ameli.fr/api/explore/v2.1/catalog/datasets"

    def __init__(self, timeout=1):
        self._timeout = timeout
        self._session = requests.Session()
        self._cache_colonnes = {}  # évite de re-sonder le schéma à chaque appel

    def get_effectifs(self, profession, departement_code, annee):
        """
        Effectifs pour une profession, un département et une année.
        """
        # Sécurité : on force les départements comme "1" à s'écrire "01"
        dept = str(departement_code).strip().zfill(2)
        
        where = (
            f"profession_sante=\"{profession}\" AND "
            f"departement=\"{dept}\" AND "
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

    def _requete(self, dataset, params, nb_essais=3):
        """Méthode privée : effectue une requête GET avec retry automatique."""
        url = f"{self.BASE_URL}/{dataset}/records"
        for essai in range(1, nb_essais + 1):
            try:
                resp = self._session.get(url, params=params, timeout=self._timeout)
                resp.raise_for_status()
                return resp.json().get("results", [])
            except requests.exceptions.Timeout:
                print(f"[AmeliAPI] Timeout essai {essai}/{nb_essais} sur {dataset}")
                if essai == nb_essais:
                    return []
            except requests.RequestException as e:
                print(f"[AmeliAPI] Erreur requête : {e}")
                return []
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
                "limit": 100
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

        return resultats_propres

    # ─────────────────────────────────────────────────────────────
    #  NOUVEAU : Pathologies (dataset "effectifs" de Data pathologies)
    # ─────────────────────────────────────────────────────────────

    #: Catégories officielles de pathologies / traitements / épisodes de soins
    #: (valeurs exactes confirmées via l'API data.ameli.fr, champ patho_niv1)
    CATEGORIES_PATHOLOGIES = [
        "Maladies cardioneurovasculaires",
        "Traitements du risque vasculaire (hors pathologies)",
        "Diabète",
        "Cancers",
        "Maladies psychiatriques",
        "Traitements psychotropes (hors pathologies)",
        "Maladies neurologiques",
        "Maladies respiratoires chroniques (hors mucoviscidose)",
        "Maladies inflammatoires ou rares ou infection VIH",
        "Insuffisance rénale chronique terminale",
        "Maladies du foie ou du pancréas (hors mucoviscidose)",
        "Affections de longue durée (dont 31 et 32) pour d'autres causes",
        "Hospitalisation pour Covid-19",
        "Maternité (avec ou sans pathologies)",
        "Traitements antalgiques ou anti-inflammatoires (hors pathologies, traitements, maternité ou hospitalisations)",
        "Hospitalisations hors pathologies repérées (avec ou sans pathologies, traitements ou maternité)",
    ]

    def get_pathologie_national(self, patho_libelle, annee, sexe="tous sexes"):
        """
        Récupère, pour une catégorie de pathologie (patho_niv1) et une année
        données, les effectifs de patients et la prévalence par département,
        France entière.

        Champs réels du dataset "effectifs" de data.ameli.fr (vérifiés en
        direct) :
            annee (texte, ex: "2019"), patho_niv1, patho_niv2, patho_niv3,
            top, cla_age_5, libelle_classe_age (ex: "tous âges"),
            sexe, libelle_sexe (ex: "tous sexes"), region, dept,
            ntop (effectif de patients concernés), npop (population totale),
            prev (prévalence, en %), niveau_prioritaire, tri.

        Le dataset fournit déjà une ligne agrégée par département avec
        libelle_classe_age="tous âges" : on l'utilise directement plutôt que
        de sommer les tranches d'âge nous-mêmes.
        """
        dataset = "effectifs"

        where = (
            f'patho_niv1="{patho_libelle}" AND '
            f'year(annee)={annee} AND '
            f'libelle_sexe="{sexe}" AND '
            f'libelle_classe_age="tous âges"'
        )

        rows = self._requete(
            dataset,
            {"where": where, "limit": 100},
        )

        resultats = []
        for r in rows:
            code_dept = str(r.get("dept", "")).strip()
            if code_dept in ("999", "", "None"):
                continue
            resultats.append({
                "departement": code_dept,
                "effectif": r.get("ntop"),
                "prevalence": r.get("prev"),
            })

        return resultats

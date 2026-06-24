from services.ameli_api import AmeliAPI

api = AmeliAPI()

print("=== 1) year(annee)=2021 seul ===")
print(api._requete("effectifs", {"where": "year(annee)=2021", "limit": 3}))

print()
print("=== 2) patho_niv1 + sexe + classe_age (SANS annee) ===")
print(api._requete("effectifs", {
    "where": 'patho_niv1="Diabète" AND libelle_sexe="tous sexes" AND libelle_classe_age="tous âges"',
    "limit": 5
}))

print()
print("=== 3) Requête complète avec year(annee) ===")
print(api._requete("effectifs", {
    "where": 'patho_niv1="Diabète" AND year(annee)=2021 AND libelle_sexe="tous sexes" AND libelle_classe_age="tous âges"',
    "limit": 5
}))
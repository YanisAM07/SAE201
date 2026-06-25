from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

# Initialisation de la base déclarative pour SQLAlchemy
Base = declarative_base()


class Region(Base):
    """Modèle représentant une région."""
    __tablename__ = "region"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), nullable=False, unique=True)
    libelle = Column(String(100), nullable=False)
    
    # Relation un-à-plusieurs avec la table departement
    departements = relationship("Departement", backref="region")

    def __repr__(self):
        return f"{self.code} {self.libelle}"


class Departement(Base):
    """Modèle représentant un département."""
    __tablename__ = "departement"
    
    id = Column(Integer, primary_key=True)
    region_id = Column(Integer, ForeignKey("region.id"), nullable=False)
    code = Column(String(3), nullable=False)
    libelle = Column(String(255), nullable=False)

    # Méthode utilitaire pour la sérialisation des données en JSON
    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "libelle": self.libelle
        }

class ProfessionSante(Base):
    """Modèle représentant une profession de santé."""
    __tablename__ = "profession_sante"
    id = Column(Integer, primary_key=True, autoincrement=True)
    libelle = Column(String(200), nullable=False, unique=True)

    def __repr__(self):
        return self.libelle


class TrancheAge(Base):
    """Modèle représentant une tranche d'âge pour les statistiques."""
    __tablename__ = "tranche_age"
    id = Column(Integer, primary_key=True, autoincrement=True)
    libelle = Column(String(100), nullable=False, unique=True)

    def __repr__(self):
        return self.libelle


class Sexe(Base):
    """Modèle représentant le genre/sexe."""
    __tablename__ = "sexe"
    id = Column(Integer, primary_key=True, autoincrement=True)
    libelle = Column(String(50), nullable=False, unique=True)

    def __repr__(self):
        return self.libelle


class TypeExercice(Base):
    """Modèle représentant le mode d'exercice médical."""
    __tablename__ = "type_exercice"
    id = Column(Integer, primary_key=True, autoincrement=True)
    libelle = Column(String(200), nullable=False, unique=True)

    def __repr__(self):
        return self.libelle


class TypeSecteur(Base):
    """Modèle représentant le secteur de convention (Secteur 1, Secteur 2, etc.)."""
    __tablename__ = "type_secteur"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), nullable=False, unique=True)
    libelle = Column(String(200), nullable=False)

    def __repr__(self):
        return f"{self.code} {self.libelle}"


class TypeHonoraire(Base):
    """Modèle représentant la hiérarchie et la classification des honoraires."""
    __tablename__ = "type_honoraire"
    id = Column(Integer, primary_key=True, autoincrement=True)
    niveau_1 = Column(String(80), nullable=False)
    niveau_2 = Column(String(80), nullable=True)
    niveau_3 = Column(String(80), nullable=True)

    # Contrainte d'unicité sur la combinaison des trois niveaux
    __table_args__ = (UniqueConstraint("niveau_1", "niveau_2", "niveau_3"),)

    def __repr__(self):
        return " > ".join(filter(None, [self.niveau_1, self.niveau_2, self.niveau_3]))


class TypePrescription(Base):
    """Modèle représentant la classification d'une prescription."""
    __tablename__ = "type_prescription"
    id = Column(Integer, primary_key=True, autoincrement=True)
    libelle = Column(String(200), nullable=False, unique=True)

    def __repr__(self):
        return self.libelle


# ---------------------------------------------------------
# Tables de faits et dimensions analytiques
# ---------------------------------------------------------

class Annee(Base):
    """
    Dimension temporelle : Année de référence des données (ex: 2019, 2020).
    Permet de filtrer et comparer les données sur plusieurs exercices.
    """
    __tablename__ = "annee"
    id = Column(Integer, primary_key=True, autoincrement=True)
    valeur = Column(Integer, nullable=False, unique=True)

    def __repr__(self):
        return str(self.valeur)


class EffectifsProfessionnel(Base):
    """
    Table de faits centrale pour la démographie.
    Associe les dimensions au nombre de professionnels recensés.
    """
    __tablename__ = "effectifs_professionnel"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Clés étrangères obligatoires
    annee_id           = Column(Integer, ForeignKey("annee.id"),            nullable=False)
    departement_id     = Column(Integer, ForeignKey("departement.id"),      nullable=False)
    profession_id      = Column(Integer, ForeignKey("profession_sante.id"), nullable=False)

    # Clés étrangères optionnelles (selon granularité de la source)
    tranche_age_id     = Column(Integer, ForeignKey("tranche_age.id"),      nullable=True)
    sexe_id            = Column(Integer, ForeignKey("sexe.id"),             nullable=True)
    type_exercice_id   = Column(Integer, ForeignKey("type_exercice.id"),    nullable=True)
    type_secteur_id    = Column(Integer, ForeignKey("type_secteur.id"),     nullable=True)

    # Mesure quantitative
    nombre = Column(Integer, nullable=False)

    # Définition des relations SQLAlchemy pour simplifier les requêtes ORM
    annee          = relationship("Annee")
    departement    = relationship("Departement")
    profession     = relationship("ProfessionSante")
    tranche_age    = relationship("TrancheAge")
    sexe           = relationship("Sexe")
    type_exercice  = relationship("TypeExercice")
    type_secteur   = relationship("TypeSecteur")

    # Contrainte d'unicité globale pour prévenir les doublons lors des imports
    __table_args__ = (
        UniqueConstraint(
            "annee_id", "departement_id", "profession_id",
            "tranche_age_id", "sexe_id", "type_exercice_id", "type_secteur_id",
            name="uq_effectifs_professionnel"
        ),
    )

    def __repr__(self):
        return (
            f"Effectifs({self.nombre} | "
            f"dept={self.departement_id} | "
            f"prof={self.profession_id} | "
            f"annee={self.annee_id})"
        )


class HonorairesStats(Base):
    """
    Table de faits pour le volet financier.
    Stocke les métriques financières par profession et zone géographique.
    """
    __tablename__ = "honoraires_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Clés étrangères
    annee_id         = Column(Integer, ForeignKey("annee.id"),              nullable=False)
    departement_id   = Column(Integer, ForeignKey("departement.id"),        nullable=False)
    profession_id    = Column(Integer, ForeignKey("profession_sante.id"),   nullable=False)
    type_honoraire_id = Column(Integer, ForeignKey("type_honoraire.id"),    nullable=True)
    type_secteur_id  = Column(Integer, ForeignKey("type_secteur.id"),       nullable=True)

    # Mesures financières (stockées en type Float pour les montants en euros)
    montant_moyen        = Column(Float, nullable=True)
    montant_total        = Column(Float, nullable=True)
    depassement_moyen    = Column(Float, nullable=True)

    # Relations ORM
    annee           = relationship("Annee")
    departement     = relationship("Departement")
    profession      = relationship("ProfessionSante")
    type_honoraire  = relationship("TypeHonoraire")
    type_secteur    = relationship("TypeSecteur")

    # Prévention des doublons lors de l'intégration des données
    __table_args__ = (
        UniqueConstraint(
            "annee_id", "departement_id", "profession_id",
            "type_honoraire_id", "type_secteur_id",
            name="uq_honoraires_stats"
        ),
    )

    def __repr__(self):
        return (
            f"Honoraires({self.montant_moyen}€ moy | "
            f"dept={self.departement_id} | "
            f"prof={self.profession_id})"
        )


class PrescriptionsStats(Base):
    """
    Table de faits dédiée aux statistiques de prescription.
    """
    __tablename__ = "prescriptions_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Clés étrangères
    annee_id              = Column(Integer, ForeignKey("annee.id"),              nullable=False)
    departement_id        = Column(Integer, ForeignKey("departement.id"),        nullable=False)
    profession_id         = Column(Integer, ForeignKey("profession_sante.id"),   nullable=False)
    type_prescription_id  = Column(Integer, ForeignKey("type_prescription.id"),  nullable=True)

    # Mesures quantitatives et financières
    nombre_actes          = Column(Integer, nullable=True)
    montant_rembourse     = Column(Float,   nullable=True)

    # Relations ORM
    annee              = relationship("Annee")
    departement        = relationship("Departement")
    profession         = relationship("ProfessionSante")
    type_prescription  = relationship("TypePrescription")

    # Contrainte d'unicité sur l'axe d'analyse complet
    __table_args__ = (
        UniqueConstraint(
            "annee_id", "departement_id", "profession_id", "type_prescription_id",
            name="uq_prescriptions_stats"
        ),
    )

    def __repr__(self):
        return (
            f"Prescriptions({self.nombre_actes} actes | "
            f"dept={self.departement_id} | "
            f"prof={self.profession_id})"
        )


class ImportLog(Base):
    """
    Journalisation (Log) des processus d'import.
    Assure la traçabilité des opérations d'ingestion depuis les sources externes.
    """
    __tablename__ = "import_log"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    date_import   = Column(Date,    nullable=False)
    table_cible   = Column(String(100), nullable=False)   # Nom de la table impactée
    nb_lignes     = Column(Integer, nullable=True)        # Volume de données traité
    statut        = Column(String(20), nullable=False)    # Indicateur de succès/échec
    message       = Column(String(500), nullable=True)    # Trace d'erreur éventuelle

    def __repr__(self):
        return f"Import({self.table_cible} | {self.date_import} | {self.statut})"
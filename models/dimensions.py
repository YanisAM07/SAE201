from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

Base = declarative_base()


class Region(Base):
    __tablename__ = "region"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), nullable=False, unique=True)
    libelle = Column(String(100), nullable=False)
    departements = relationship("Departement", backref="region")

    def __repr__(self):
        return f"{self.code} {self.libelle}"


class Departement(Base):
    __tablename__ = "departement"
    
    id = Column(Integer, primary_key=True)
    region_id = Column(Integer, ForeignKey("region.id"), nullable=False)
    code = Column(String(3), nullable=False)
    libelle = Column(String(255), nullable=False)

    #rajout
    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "libelle": self.libelle
        }

class ProfessionSante(Base):
    __tablename__ = "profession_sante"
    id = Column(Integer, primary_key=True, autoincrement=True)
    libelle = Column(String(200), nullable=False, unique=True)

    def __repr__(self):
        return self.libelle


class TrancheAge(Base):
    __tablename__ = "tranche_age"
    id = Column(Integer, primary_key=True, autoincrement=True)
    libelle = Column(String(100), nullable=False, unique=True)

    def __repr__(self):
        return self.libelle


class Sexe(Base):
    __tablename__ = "sexe"
    id = Column(Integer, primary_key=True, autoincrement=True)
    libelle = Column(String(50), nullable=False, unique=True)

    def __repr__(self):
        return self.libelle


class TypeExercice(Base):
    __tablename__ = "type_exercice"
    id = Column(Integer, primary_key=True, autoincrement=True)
    libelle = Column(String(200), nullable=False, unique=True)

    def __repr__(self):
        return self.libelle


class TypeSecteur(Base):
    __tablename__ = "type_secteur"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), nullable=False, unique=True)
    libelle = Column(String(200), nullable=False)

    def __repr__(self):
        return f"{self.code} {self.libelle}"


class TypeHonoraire(Base):
    __tablename__ = "type_honoraire"
    id = Column(Integer, primary_key=True, autoincrement=True)
    niveau_1 = Column(String(80), nullable=False)
    niveau_2 = Column(String(80), nullable=True)
    niveau_3 = Column(String(80), nullable=True)

    __table_args__ = (UniqueConstraint("niveau_1", "niveau_2", "niveau_3"),)

    def __repr__(self):
        return " > ".join(filter(None, [self.niveau_1, self.niveau_2, self.niveau_3]))


class TypePrescription(Base):
    __tablename__ = "type_prescription"
    id = Column(Integer, primary_key=True, autoincrement=True)
    libelle = Column(String(200), nullable=False, unique=True)

    def __repr__(self):
        return self.libelle


# ─────────────────────────────────────────────
#  NOUVELLES TABLES
# ─────────────────────────────────────────────

class Annee(Base):
    """
    Année de référence des données (ex: 2019, 2020, 2021...).
    Permet de filtrer et comparer les données sur plusieurs années.
    """
    __tablename__ = "annee"
    id = Column(Integer, primary_key=True, autoincrement=True)
    valeur = Column(Integer, nullable=False, unique=True)

    def __repr__(self):
        return str(self.valeur)


class EffectifsProfessionnel(Base):
    """
    Table de faits centrale.
    Relie toutes les dimensions pour stocker le nombre de professionnels
    de santé selon chaque critère issu de l'API Data Ameli.
    """
    __tablename__ = "effectifs_professionnel"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Dimensions obligatoires
    annee_id           = Column(Integer, ForeignKey("annee.id"),            nullable=False)
    departement_id     = Column(Integer, ForeignKey("departement.id"),      nullable=False)
    profession_id      = Column(Integer, ForeignKey("profession_sante.id"), nullable=False)

    # Dimensions optionnelles (peuvent être NULL selon la ligne API)
    tranche_age_id     = Column(Integer, ForeignKey("tranche_age.id"),      nullable=True)
    sexe_id            = Column(Integer, ForeignKey("sexe.id"),             nullable=True)
    type_exercice_id   = Column(Integer, ForeignKey("type_exercice.id"),    nullable=True)
    type_secteur_id    = Column(Integer, ForeignKey("type_secteur.id"),     nullable=True)

    # Mesure principale
    nombre = Column(Integer, nullable=False)

    # Relations (pour accès ORM simplifié dans les services)
    annee          = relationship("Annee")
    departement    = relationship("Departement")
    profession     = relationship("ProfessionSante")
    tranche_age    = relationship("TrancheAge")
    sexe           = relationship("Sexe")
    type_exercice  = relationship("TypeExercice")
    type_secteur   = relationship("TypeSecteur")

    # Évite les doublons si l'import est relancé
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
    Statistiques d'honoraires par profession, département et année.
    Stocke les montants moyens issus de Data Ameli (honoraires totaux,
    dépassements, remboursements).
    """
    __tablename__ = "honoraires_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)

    annee_id         = Column(Integer, ForeignKey("annee.id"),              nullable=False)
    departement_id   = Column(Integer, ForeignKey("departement.id"),        nullable=False)
    profession_id    = Column(Integer, ForeignKey("profession_sante.id"),   nullable=False)
    type_honoraire_id = Column(Integer, ForeignKey("type_honoraire.id"),    nullable=True)
    type_secteur_id  = Column(Integer, ForeignKey("type_secteur.id"),       nullable=True)

    # Montants en euros
    montant_moyen        = Column(Float, nullable=True)
    montant_total        = Column(Float, nullable=True)
    depassement_moyen    = Column(Float, nullable=True)

    annee           = relationship("Annee")
    departement     = relationship("Departement")
    profession      = relationship("ProfessionSante")
    type_honoraire  = relationship("TypeHonoraire")
    type_secteur    = relationship("TypeSecteur")

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
    Statistiques de prescriptions par profession, département et année.
    Nombre moyen d'actes prescrits, montant remboursé, etc.
    """
    __tablename__ = "prescriptions_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)

    annee_id              = Column(Integer, ForeignKey("annee.id"),              nullable=False)
    departement_id        = Column(Integer, ForeignKey("departement.id"),        nullable=False)
    profession_id         = Column(Integer, ForeignKey("profession_sante.id"),   nullable=False)
    type_prescription_id  = Column(Integer, ForeignKey("type_prescription.id"),  nullable=True)

    nombre_actes          = Column(Integer, nullable=True)
    montant_rembourse     = Column(Float,   nullable=True)

    annee              = relationship("Annee")
    departement        = relationship("Departement")
    profession         = relationship("ProfessionSante")
    type_prescription  = relationship("TypePrescription")

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
    Journal des imports de données depuis l'API Data Ameli.
    Permet de savoir quand les données ont été chargées, combien de lignes
    ont été insérées, et si l'import s'est bien passé.
    Utile pour la maintenabilité et le debug.
    """
    __tablename__ = "import_log"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    date_import   = Column(Date,    nullable=False)
    table_cible   = Column(String(100), nullable=False)   # ex: "effectifs_professionnel"
    nb_lignes     = Column(Integer, nullable=True)
    statut        = Column(String(20), nullable=False)    # "succes" ou "erreur"
    message       = Column(String(500), nullable=True)    # détail erreur si besoin

    def __repr__(self):
        return f"Import({self.table_cible} | {self.date_import} | {self.statut})"

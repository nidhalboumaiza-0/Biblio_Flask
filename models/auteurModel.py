from db import db


class AuteurModel(db.Model):
    __tablename__ = "auteurs"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)

    livres = db.relationship('LivreModel', back_populates='auteur')
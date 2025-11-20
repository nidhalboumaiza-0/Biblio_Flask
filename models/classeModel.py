from db import db


class ClasseModel(db.Model):
    __tablename__ = "classes"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(80), nullable=False, unique=True)

    adherents = db.relationship('AdherentModel', back_populates='classe')


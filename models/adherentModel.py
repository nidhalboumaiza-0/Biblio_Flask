import bcrypt
from db import db
from sqlalchemy.ext.hybrid import hybrid_property

class AdherentModel(db.Model):
    __tablename__ = "adherents"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    adresse = db.Column(db.String(200), nullable=False)
    date_naissance = db.Column(db.Date, nullable=False)
    num_carte_identite = db.Column(db.String(20), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    _password = db.Column("password", db.String(128), nullable=False)  # Private field for storing the hashed password
    nbr_conx = db.Column(db.Integer, default=0)
    password_changed = db.Column(db.Boolean, default=False)
    nbr_emprunts = db.Column(db.Integer, default=0)
    classe_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    gender = db.Column(db.String(1), nullable=False, default="G")
    role = db.Column(db.String(20), default="adherent")

    emprunts = db.relationship('EmpruntModel', back_populates='adherent')
    classe = db.relationship('ClasseModel', back_populates='adherents')

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, plain_text_password):
        # Hash the password using bcrypt
        salt = bcrypt.gensalt()
        self._password = bcrypt.hashpw(plain_text_password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, plain_text_password):
        # Verify the password using bcrypt
        return bcrypt.checkpw(plain_text_password.encode('utf-8'), self._password.encode('utf-8'))
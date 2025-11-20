from marshmallow import Schema, fields, validate

# -------------------- Adherent Schemas --------------------

class PlainAdherentSchema(Schema):
    id = fields.Int(dump_only=True)
    nom = fields.Str(required=True)


class AdherentSchema(Schema):
    id = fields.Int(dump_only=True)
    nom = fields.Str(required=True)
    email = fields.Email(required=True)
    adresse = fields.Str(required=True)
    date_naissance = fields.Date(required=True)
    num_carte_identite = fields.Str(required=True)
    username = fields.Str(required=True)
    password = fields.Str(load_only=True, required=True)  # Password should not be dumped
    nbr_conx = fields.Int(dump_only=True)
    password_changed = fields.Bool(dump_only=True)
    nbr_emprunts = fields.Int(dump_only=True)
    classe_id = fields.Int(required=True, load_only=True)
    gender = fields.Str(
        required=True,
        validate=validate.OneOf(
            ["G", "F"],
            error="Le genre doit être 'G' (Homme) ou 'F' (Femme)."
        )
    )
    classe = fields.Nested("PlainClasseSchema", dump_only=True)  # Simplified Classe schema
    emprunts = fields.List(fields.Nested("PlainEmpruntSchema"), dump_only=True)  # Simplified Emprunt schema


class AdherentUpdateSchema(Schema):
    nom = fields.Str()
    email = fields.Email()
    adresse = fields.Str()
    date_naissance = fields.Date()
    num_carte_identite = fields.Str()
    username = fields.Str()
    password = fields.Str(load_only=True)  # Password should not be dumped
    classe_id = fields.Int()
    gender = fields.Str(
        validate=validate.OneOf(
            ["G", "F"],
            error="Le genre doit être 'G' (Homme) ou 'F' (Femme)."
        )
    )

# -------------------- Auteur Schemas --------------------

class PlainAuteurSchema(Schema):
    id = fields.Int(dump_only=True)
    nom = fields.Str(required=True)
    prenom = fields.Str(required=True)


class AuteurSchema(Schema):
    id = fields.Int(dump_only=True)
    nom = fields.Str(required=True)
    prenom = fields.Str(required=True)
    livres = fields.List(fields.Nested("PlainLivreSchema"), dump_only=True)  # Simplified Livre schema


class AuteurUpdateSchema(Schema):
    nom = fields.Str()
    prenom = fields.Str()

# -------------------- Classe Schemas --------------------

class PlainClasseSchema(Schema):
    id = fields.Int(dump_only=True)
    nom = fields.Str(required=True)


class ClasseSchema(PlainClasseSchema):
    adherents = fields.List(fields.Nested("PlainAdherentSchema"), dump_only=True)  # Simplified Adherent schema

# -------------------- Livre Schemas --------------------

class PlainLivreSchema(Schema):
    id = fields.Int(dump_only=True)
    titre = fields.Str(required=True)
    nbre_pages = fields.Int(required=True)
    nbre_exemplaires = fields.Int(dump_only=True)
    disponible = fields.Bool(dump_only=True)


class LivreSchema(PlainLivreSchema):
    code_auteur = fields.Int(required=True, load_only=True)
    auteur = fields.Nested("PlainAuteurSchema", dump_only=True)  # Simplified Auteur schema
    emprunts = fields.List(fields.Nested("PlainEmpruntSchema"), dump_only=True)
    genres = fields.List(fields.Nested("PlainGenreSchema"), dump_only=True)


class LivreUpdateSchema(Schema):
    titre = fields.Str()
    nbre_pages = fields.Int()
    nbre_exemplaires = fields.Int()
    disponible = fields.Bool()

# -------------------- Emprunt Schemas --------------------

class PlainEmpruntSchema(Schema):
    id = fields.Int(dump_only=True)
    date_debut = fields.Date(required=True)
    date_retour = fields.Date()


class EmpruntSchema(PlainEmpruntSchema):
    adherent_id = fields.Int(required=True, load_only=True)
    livre_id = fields.Int(required=True, load_only=True)
    retourner = fields.Bool(dump_only=True)
    adherent = fields.Nested("PlainAdherentSchema", dump_only=True)  # Simplified Adherent schema
    livre = fields.Nested("PlainLivreSchema", dump_only=True)  # Simplified Livre schema


class EmpruntCreateSchema(Schema):
    date_debut = fields.Date(required=True)
    adherent_id = fields.Int(required=True)
    livre_id = fields.Int(required=True)

# -------------------- Genre Schemas --------------------

class PlainGenreSchema(Schema):
    id = fields.Int(dump_only=True)
    nom = fields.Str(required=True)


class GenreSchema(PlainGenreSchema):
    livres = fields.List(fields.Nested("PlainLivreSchema"), dump_only=True)  # Simplified Livre schema


class GenreUpdateSchema(Schema):
    nom = fields.Str(required=True)
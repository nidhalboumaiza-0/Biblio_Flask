from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import AuteurModel
from schemas import AuteurSchema, AuteurUpdateSchema

# Create a Blueprint for auteurs
blp = Blueprint("Auteurs", __name__, description="Operations on authors")


@blp.route("/auteur/<int:auteur_id>")
class Auteur(MethodView):
    @blp.response(200, AuteurSchema)
    def get(self, auteur_id):
        """Get an author by their ID."""
        auteur = AuteurModel.query.get_or_404(auteur_id)
        return auteur

    def delete(self, auteur_id):
        """Delete an author by their ID."""
        auteur = AuteurModel.query.get_or_404(auteur_id)
        try:
            db.session.delete(auteur)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting the author.")
        return {"message": "Author deleted successfully."}

    @blp.arguments(AuteurUpdateSchema)
    @blp.response(200, AuteurSchema)
    def put(self, auteur_data, auteur_id):
        """Update an author by their ID."""
        auteur = AuteurModel.query.get(auteur_id)

        if auteur:
            for key, value in auteur_data.items():
                setattr(auteur, key, value)
        else:
            auteur = AuteurModel(id=auteur_id, **auteur_data)

        try:
            db.session.add(auteur)
            db.session.commit()
        except IntegrityError:
            abort(400, message="An author with this ID already exists.")
        except SQLAlchemyError:
            abort(500, message="An error occurred while updating the author.")

        return auteur


@blp.route("/auteur")
class AuteurList(MethodView):
    @blp.response(200, AuteurSchema(many=True))
    def get(self):
        """Get a list of all authors, sorted alphabetically by last name."""
        auteurs = AuteurModel.query.order_by(AuteurModel.nom).all()
        return auteurs

    @blp.arguments(AuteurSchema)
    @blp.response(201, AuteurSchema)
    def post(self, auteur_data):
        """Create a new author."""
        auteur = AuteurModel(**auteur_data)

        try:
            db.session.add(auteur)
            db.session.commit()
        except IntegrityError:
            abort(400, message="An author with this ID already exists.")
        except SQLAlchemyError:
            abort(500, message="An error occurred while creating the author.")

        return auteur
    
@blp.route("/auteur/find/<string:name>")
class AuteurByName(MethodView):
    @blp.response(200, AuteurSchema(many=True))
    def get(self, name):
        """Find authors by their first name, last name, or both."""
        auteurs = AuteurModel.query.filter(
            or_(
                AuteurModel.nom.like(f"%{name}%"),
                AuteurModel.prenom.like(f"%{name}%")
            )
        ).all()

        if not auteurs:
            abort(404, message=f"No authors found with name containing '{name}'.")

        return auteurs
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import LivreModel
from schemas import AdherentSchema, LivreSchema, LivreUpdateSchema
from models import AuteurModel
from schemas import AuteurSchema
# Create a Blueprint for livres
blp = Blueprint("Livres", __name__, description="Operations on books")


@blp.route("/livre/<int:livre_id>")
class Livre(MethodView):
    @blp.response(200, LivreSchema)
    def get(self, livre_id):
        """Get a book by its ID."""
        livre = LivreModel.query.get_or_404(livre_id)
        return livre

    def delete(self, livre_id):
        """Delete a book by its ID."""
        livre = LivreModel.query.get_or_404(livre_id)
        db.session.delete(livre)
        db.session.commit()
        return {"message": "Book deleted."}

    @blp.arguments(LivreUpdateSchema)
    @blp.response(200, LivreSchema)
    def put(self, livre_data, livre_id):
        """Update a book by its ID."""
        livre = LivreModel.query.get(livre_id)

        if livre:
            livre.titre = livre_data.get("titre", livre.titre)
            livre.nbre_pages = livre_data.get("nbre_pages", livre.nbre_pages)
            livre.nbre_exemplaires = livre_data.get("nbre_exemplaires", livre.nbre_exemplaires)
            livre.disponible = livre_data.get("disponible", livre.disponible)
        else:
            livre = LivreModel(id=livre_id, **livre_data)

        db.session.add(livre)
        db.session.commit()

        return livre


@blp.route("/livre")
class LivreList(MethodView):
    @blp.response(200, LivreSchema(many=True))
    def get(self):
        """Get a list of all books."""
        return LivreModel.query.all()

    @blp.arguments(LivreSchema)
    @blp.response(201, LivreSchema)
    def post(self, livre_data):
        """Create a new book."""
        livre = LivreModel(**livre_data)

        try:
            db.session.add(livre)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the book.")

        return livre


@blp.route("/livre/find/<string:title>")
class LivreByTitle(MethodView):
    @blp.response(200, LivreSchema(many=True))
    def get(self, title):
        """Find books by their title."""
        livres = LivreModel.query.filter(LivreModel.titre.like(f"%{title}%")).all()
        if not livres:
            abort(404, message=f"No books found with title containing '{title}'.")
        return livres
    

@blp.route("/livre/auteur/<string:auteur_name>")
class LivreByAuteur(MethodView):
    @blp.response(200, LivreSchema(many=True))
    def get(self, auteur_name):
        """Find books by their author."""
        livres = LivreModel.query.join(AuteurModel).filter(
            (AuteurModel.nom.like(f"%{auteur_name}%")) | (AuteurModel.prenom.like(f"%{auteur_name}%"))
        ).all()
        if not livres:
            abort(404, message=f"No books found for author '{auteur_name}'.")
        return livres
    

@blp.route("/livre/<int:livre_id>/emprunteurs")
class LivreEmprunteurs(MethodView):
    @blp.response(200, AdherentSchema(many=True))
    def get(self, livre_id):
        
        livre = LivreModel.query.get_or_404(livre_id)

        
        emprunteurs = [emprunt.adherent for emprunt in livre.emprunts]

        if not emprunteurs:
            abort(404, message=f"No borrowers found for the book with name {livre.titre}.")

        return emprunteurs

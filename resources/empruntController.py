from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import func
from datetime import datetime, timedelta

from db import db
from models import EmpruntModel, LivreModel, AdherentModel
from schemas import EmpruntSchema, EmpruntCreateSchema, LivreSchema, AdherentSchema

# Create a Blueprint for emprunts
blp = Blueprint("Emprunts", __name__, description="Operations on borrowings")


@blp.route("/emprunt/<int:emprunt_id>")
class Emprunt(MethodView):
    @blp.response(200, EmpruntSchema)
    def get(self, emprunt_id):
        """Get an emprunt by its ID."""
        emprunt = EmpruntModel.query.get_or_404(emprunt_id)
        return emprunt

    def delete(self, emprunt_id):
        """Delete an emprunt by its ID."""
        emprunt = EmpruntModel.query.get_or_404(emprunt_id)
        try:
            livre = LivreModel.query.get_or_404(emprunt.livre_id)
            livre.nbre_exemplaires += 1
            db.session.delete(emprunt)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting the borrowing record.")
        return {"message": "Borrowing record deleted successfully."}


@blp.route("/emprunt")
class EmpruntList(MethodView):
    @blp.response(200, EmpruntSchema(many=True))
    def get(self):
        """Get a list of all borrowings."""
        emprunts = EmpruntModel.query.all()
        return emprunts

    @blp.arguments(EmpruntCreateSchema)
    @blp.response(201, EmpruntSchema)
    def post(self, emprunt_data):
        """Create a new borrowing record."""
        # Check if the book is available
        livre = LivreModel.query.get_or_404(emprunt_data["livre_id"])
        if livre.nbre_exemplaires <= 0:
            abort(400, message="This book is not available for borrowing.")

        # Automatically set the borrowing date to the current date
        emprunt_data["date_debut"] = datetime.utcnow().date()
        # Automatically set the return date to 15 days after the borrowing date
        emprunt_data["date_retour"] = emprunt_data["date_debut"] + timedelta(days=15)

        # Create the borrowing record
        emprunt = EmpruntModel(**emprunt_data)
        livre.nbre_exemplaires -= 1  # Decrease the number of available copies

        try:
            db.session.add(emprunt)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while creating the borrowing record.")

        return emprunt


@blp.route("/emprunt/<int:emprunt_id>/return")
class ReturnBook(MethodView):
    @blp.response(200, EmpruntSchema)
    def put(self, emprunt_id):
        """Mark a book as returned."""
        emprunt = EmpruntModel.query.get_or_404(emprunt_id)

        if emprunt.retourner:
            abort(400, message="This book has already been returned.")

        emprunt.retourner = True
        emprunt.date_retour = datetime.utcnow()

        # Increase the number of available copies for the book
        livre = LivreModel.query.get_or_404(emprunt.livre_id)
        livre.nbre_exemplaires += 1

        try:
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while updating the return status.")

        return emprunt


@blp.route("/emprunts/non-retournes")
class NonReturnedBooks(MethodView):
    @blp.response(200, LivreSchema(many=True))
    def get(self):
        """Get a list of books that have not been returned."""
        non_returned_emprunts = EmpruntModel.query.filter_by(retourner=False).all()
        if not non_returned_emprunts:
            abort(404, message="No non-returned books found.")

        non_returned_books = [emprunt.livre for emprunt in non_returned_emprunts]
        return non_returned_books


@blp.route("/emprunts/retardataires")
class OverdueBorrowers(MethodView):
    @blp.response(200, AdherentSchema(many=True))
    def get(self):
        """Get a list of adherents who have overdue books."""
        today = datetime.utcnow()
        overdue_emprunts = (
            EmpruntModel.query.filter(EmpruntModel.retourner == False)
            .filter(EmpruntModel.date_debut + timedelta(days=15) < today)
            .all()
        )
        overdue_borrowers = list({emprunt.adherent for emprunt in overdue_emprunts})

        if not overdue_borrowers:
            abort(404, message="No overdue borrowers found.")

        return overdue_borrowers


@blp.route("/emprunts/stats/most-borrowed-books")
class MostBorrowedBooks(MethodView):
    @blp.response(200, LivreSchema(many=True))
    def get(self):
        """Get a list of the most borrowed books."""
        most_borrowed_books = (
            db.session.query(LivreModel, func.count(EmpruntModel.id).label("borrow_count"))
            .join(EmpruntModel, LivreModel.id == EmpruntModel.livre_id)
            .group_by(LivreModel.id)
            .order_by(func.count(EmpruntModel.id).desc())
            .limit(5)
            .all()
        )

        if not most_borrowed_books:
            abort(404, message="No borrowing data available.")

        return [{"book": book, "borrow_count": borrow_count} for book, borrow_count in most_borrowed_books]
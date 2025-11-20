from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import func

from db import db
from models import AdherentModel, EmpruntModel
from schemas import AdherentSchema, LivreSchema , AdherentUpdateSchema

# Create a Blueprint for adherents
blp = Blueprint("Adherents", __name__, description="Operations on adherents")


@blp.route("/adherent/<int:adherent_id>")
class Adherent(MethodView):
    @blp.response(200, AdherentSchema)
    def get(self, adherent_id):
        """Get an adherent by their ID."""
        adherent = AdherentModel.query.get_or_404(adherent_id)
        return adherent

    def delete(self, adherent_id):
        """Delete an adherent by their ID."""
        adherent = AdherentModel.query.get_or_404(adherent_id)
        try:
            db.session.delete(adherent)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting the adherent.")
        return {"message": "Adherent deleted successfully."}

    @blp.arguments(AdherentUpdateSchema)
    @blp.response(200, AdherentSchema)
    def put(self, adherent_data, adherent_id):
        """Update an adherent by their ID."""
        # Retrieve the adherent instance from the database
        adherent = AdherentModel.query.get(adherent_id)

        if adherent:
            # Update only the fields provided in adherent_data
            for key, value in adherent_data.items():
                if hasattr(adherent, key) and value is not None:  # Ensure the attribute exists and value is not None
                    setattr(adherent, key, value)
        else:
            # If the adherent does not exist, create a new one with the provided data
            adherent = AdherentModel(id=adherent_id, **adherent_data)

        try:
            # Add the adherent to the session and commit changes
            db.session.add(adherent)
            db.session.commit()
        except IntegrityError:
            abort(400, message="An adherent with this email, username, or ID already exists.")
        except SQLAlchemyError:
            abort(500, message="An error occurred while updating the adherent.")

        return adherent


@blp.route("/adherent")
class AdherentList(MethodView):
    @blp.response(200, AdherentSchema(many=True))
    def get(self):
        """Get a list of all adherents, sorted alphabetically by name."""
        adherents = AdherentModel.query.order_by(AdherentModel.nom).all()
        return adherents

    @blp.arguments(AdherentSchema)
    @blp.response(201, AdherentSchema)
    def post(self, adherent_data):
        """Create a new adherent."""
        # Set the default password if none is provided
        adherent_data["password"] = adherent_data.get("password", "123456")

        # Create the adherent instance
        adherent = AdherentModel(**adherent_data)

        try:
            db.session.add(adherent)
            db.session.commit()
        except IntegrityError as e:
            if "email" in str(e.orig):
                abort(400, message="An adherent with this email already exists.")
            elif "username" in str(e.orig):
                abort(400, message="An adherent with this username already exists.")
            elif "num_carte_identite" in str(e.orig):
                abort(400, message="An adherent with this ID card number already exists.")
            else:
                abort(400, message="An adherent with this email, username, or ID already exists.")
        except SQLAlchemyError:
            abort(500, message="An error occurred while creating the adherent.")

        return adherent
@blp.route("/adherent/<int:adherent_id>/emprunts")
class AdherentEmprunts(MethodView):
    @blp.response(200, LivreSchema(many=True))
    def get(self, adherent_id):
        """Get the list of books borrowed by an adherent."""
        adherent = AdherentModel.query.get_or_404(adherent_id)
        emprunts = [emprunt.livre for emprunt in adherent.emprunts]

        if not emprunts:
            abort(404, message=f"No books borrowed by adherent {adherent.nom}.")

        return emprunts


@blp.route("/adherent/stats/top")
class TopAdherents(MethodView):
    @blp.response(200, AdherentSchema(many=True))
    def get(self):
        """Get the top adherents who borrowed the most books."""
        top_adherents = (
            AdherentModel.query.order_by(AdherentModel.nbr_emprunts.desc())
            .limit(5)
            .all()
        )
        if not top_adherents:
            abort(404, message="No adherents found.")
        return top_adherents


@blp.route("/adherent/stats/retardataires")
class Retardataires(MethodView):
    @blp.response(200, AdherentSchema(many=True))
    def get(self):
        """Get the list of adherents who have overdue books."""
        from datetime import datetime, timedelta

        today = datetime.utcnow()

        # Query for overdue emprunts where the book has not been returned (retourner=False)
        overdue_emprunts = (
            EmpruntModel.query.filter(EmpruntModel.retourner == False)  # Not returned
            .filter(EmpruntModel.date_debut + timedelta(days=15) < today)  # Overdue
            .all()
        )

        # Get the adherents associated with the overdue emprunts
        retardataires = list({emprunt.adherent for emprunt in overdue_emprunts})

        # If no overdue adherents are found, return a 404 error
        if not retardataires:
            abort(404, message="No overdue adherents found.")

        return retardataires
    


@blp.route("/adherent/stats/gender-borrowing")
class GenderBorrowingStats(MethodView):
    def get(self):
        """Calculate the percentage of boys and girls who borrow books."""
        # Total number of adherents who borrowed books
        total_borrowers = db.session.query(AdherentModel).join(EmpruntModel).distinct().count()

        if total_borrowers == 0:
            abort(404, message="No borrowing data available.")

        # Count male borrowers
        male_borrowers = (
            db.session.query(AdherentModel)
            .join(EmpruntModel)
            .filter(AdherentModel.gender == "G")
            .distinct()
            .count()
        )

        # Count female borrowers
        female_borrowers = (
            db.session.query(AdherentModel)
            .join(EmpruntModel)
            .filter(AdherentModel.gender == "F")
            .distinct()
            .count()
        )

        # Calculate percentages
        male_percentage = (male_borrowers / total_borrowers) * 100
        female_percentage = (female_borrowers / total_borrowers) * 100

        return {
            "total_borrowers": total_borrowers,
            "male_borrowers": male_borrowers,
            "female_borrowers": female_borrowers,
            "male_percentage": round(male_percentage, 2),
            "female_percentage": round(female_percentage, 2),
        }
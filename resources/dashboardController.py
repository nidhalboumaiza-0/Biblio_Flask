from flask import jsonify
from datetime import datetime, timedelta

from sqlalchemy import func
from models import AdherentModel, EmpruntModel, LivreModel
from flask_smorest import Blueprint, abort
from db import db

blp = Blueprint("Dashboard", __name__, description="Operations on classes")

@blp.route("/dashboard/stats")
def dashboard_stats():
    # Total Books
    total_books = LivreModel.query.count()

    # Total Members
    total_members = AdherentModel.query.count()

    # Active Borrowings
    active_borrowings = EmpruntModel.query.filter_by(retourner=False).count()

    # Overdue Books
    today = datetime.utcnow()
    overdue_books = EmpruntModel.query.filter(
        EmpruntModel.retourner == False,
        EmpruntModel.date_debut + timedelta(days=15) < today
    ).count()

    # Top Borrowers
    top_borrowers = (
        db.session.query(AdherentModel.nom, func.count(EmpruntModel.id).label('count'))
        .join(EmpruntModel, AdherentModel.id == EmpruntModel.adherent_id)
        .group_by(AdherentModel.id)
        .order_by(func.count(EmpruntModel.id).desc())
        .limit(5)
        .all()
    )
    top_borrowers = [{"name": borrower.nom, "count": borrower.count} for borrower in top_borrowers]

    # Gender Distribution
    male_borrowers = AdherentModel.query.filter_by(gender="G").count()
    female_borrowers = AdherentModel.query.filter_by(gender="F").count()
    gender_distribution = {"male": male_borrowers, "female": female_borrowers}

    # Recent Borrowings
    recent_borrowings = (
        EmpruntModel.query.join(LivreModel).join(AdherentModel)
        .order_by(EmpruntModel.date_debut.desc())
        .limit(5)
        .all()
    )
    recent_borrowings = [
        {
            "id": borrowing.id,
            "bookTitle": borrowing.livre.titre,
            "memberName": borrowing.adherent.nom,
            "borrowDate": borrowing.date_debut.isoformat(),
        }
        for borrowing in recent_borrowings
    ]

    return jsonify({
        "totalBooks": total_books,
        "totalMembers": total_members,
        "activeBorrowings": active_borrowings,
        "overdueBooks": overdue_books,
        "topBorrowers": top_borrowers,
        "genderDistribution": gender_distribution,
        "recentBorrowings": recent_borrowings,
    })
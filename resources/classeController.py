from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from db import db
from models import ClasseModel
from schemas import ClasseSchema, PlainClasseSchema

blp = Blueprint("Classes", __name__, description="Operations on classes")


@blp.route("/classe/<int:classe_id>")
class Classe(MethodView):
    # @jwt_required()
    @blp.response(200, ClasseSchema)
    def get(self, classe_id):
        """Get a single class by ID"""
        classe = ClasseModel.query.get_or_404(classe_id)
        return classe

    def delete(self, classe_id):
        """Delete a class by ID"""
        classe = ClasseModel.query.get_or_404(classe_id)
        db.session.delete(classe)
        db.session.commit()
        return {"message": "Class deleted."}

    @blp.arguments(ClasseSchema)
    @blp.response(200, ClasseSchema)
    def put(self, classe_data, classe_id):
        """Update a class by ID"""
        classe = ClasseModel.query.get(classe_id)

        if classe:
            classe.nom = classe_data["nom"]
        else:
            classe = ClasseModel(id=classe_id, **classe_data)

        db.session.add(classe)
        db.session.commit()

        return classe


@blp.route("/classe")
class ClasseList(MethodView):
    @jwt_required()
    @blp.response(200, ClasseSchema(many=True))
    def get(self):
        """Get all classes"""
        return ClasseModel.query.all()

    @blp.arguments(ClasseSchema)
    @blp.response(201, ClasseSchema)
    def post(self, classe_data):
        """Create a new class"""
        classe = ClasseModel(**classe_data)

        try:
            db.session.add(classe)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the class.")

        return classe
    
@blp.route("/classe/name/<string:classe_name>")
class ClasseByName(MethodView):
    @blp.response(200, ClasseSchema)
    def get(self, classe_name):
        """Get a class by its name"""
        classe = ClasseModel.find_by_name(classe_name)
        if not classe:
            abort(404, message=f"Classe '{classe_name}' not found.")
        return classe

from flask import request, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    set_access_cookies,
    unset_jwt_cookies,
    get_jwt
)
from werkzeug.security import check_password_hash, generate_password_hash
from db import db
from models import AdherentModel
from schemas import AdherentSchema
from functools import wraps
auth_blp = Blueprint("Auth", __name__, description="Authentication operations")


@auth_blp.route("/login")
class Login(MethodView):
    def post(self):
        """Authenticate a user and provide a JWT."""
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        # Find the user
        user = AdherentModel.query.filter_by(username=username).first()
        if not user or not user.check_password(password):  # Use the check_password method
            abort(401, message="Invalid username or password.")

        # Create a JWT token
        print (user.role)
        access_token = create_access_token(identity=username)
        # access_token = create_access_token(identity={"id": user.id, "role": user.role})
        response = jsonify(
            access_token=access_token,
            user_id=user.id,
            user_role=user.role
        )
        set_access_cookies(response, access_token)
        return response


@auth_blp.route("/change-password")
class ChangePassword(MethodView):
    @jwt_required()
    def post(self):
        """Change the password of the authenticated user."""
        current_user_id = get_jwt_identity()
        user = AdherentModel.query.get_or_404(current_user_id)

        data = request.get_json()
        old_password = data.get("old_password")
        new_password = data.get("new_password")

        # Verify old password
        if not user.check_password(old_password):
            abort(400, message="Old password is incorrect.")

        # Update password
        user.password = new_password  # This will automatically hash the password
        user.password_changed = True
        db.session.commit()

        return {"message": "Password updated successfully."}

@auth_blp.route("/logout")
class Logout(MethodView):
    @jwt_required()
    def post(self):
        """Logout the user by removing the JWT."""
        response = jsonify({"message": "Logged out successfully."})
        unset_jwt_cookies(response)
        return response


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()  # Récupère les données du JWT
        if claims.get("role") != "admin":
            return jsonify({"msg": "Admins only!"}), 403
        return fn(*args, **kwargs)
    return wrapper
from flask import jsonify

from app.api.auth.helpers import generate_salt, hash_password
from app.db.models import User, db


def signup(mobile, username, password):
    try:
        if not all([mobile, username, password]):
            return jsonify({"status": False, "message": "All fields are required"}), 400

        existing_user = User.query.filter_by(mobile=mobile).first()

        if existing_user:
            return jsonify({"status": False, "message": "User already exists"}), 400
        salt = generate_salt()

        hashed_password = hash_password(password, salt)
        new_user = User(
            mobile=mobile, username=username, password=hashed_password, salt=salt
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"status": True, "message": "User created successfully"}), 201
    except Exception as e:
        print("[Error] error while signing up: ", e)
        db.session.rollback()
        return jsonify({"status": False, "message": "internal server error"}), 500

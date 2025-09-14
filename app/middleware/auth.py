from functools import wraps
from flask import request, jsonify, current_app
import jwt
from app.db.models import User


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check if 'Authorization' header is present
        if "Authorization" in request.headers:
            # The header should be in the format 'Bearer <token>'
            auth_header = request.headers["Authorization"]
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"message": "Bearer token malformed"}), 401

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            # Decode the token using your secret key
            data = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            # Find the user based on the 'sub' claim in the token
            current_user = User.query.filter_by(userid=data["sub"]).first()
            if not current_user:
                return jsonify({"message": "User not found"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token is invalid!"}), 401

        # Pass the user object to the decorated route
        return f(current_user, *args, **kwargs)

    return decorated

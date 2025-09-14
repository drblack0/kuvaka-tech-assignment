import os
from re import L

from dotenv import load_dotenv
from flask import request, Flask
from app.api.auth.signup import signup
from app.api.auth.otpService import (
    change_password,
    forget_password,
    send_otp,
    verif_otp,
)
from app.api.chatroom.messages import generate_message
from app.api.communications.chatroom import (
    create_chatroom,
    get_all_chatrooms,
    get_chatroom_details,
)
from app.api.subscription.subscription import (
    create_pro_subscription,
    get_subscription_status,
    stripe_webhook,
)
from app.api.user.user import user_details
from app.middleware.auth import token_required

load_dotenv()
app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")


@app.route("/auth/signup", methods=["POST"])
def signup_route():
    data = request.get_json()
    return signup(data.get("mobile"), data.get("username"), data.get("password"))


@app.route("/auth/send-otp", methods=["POST"])
def send_otp_route():
    data = request.get_json()
    return send_otp(data.get("mobile"))


@app.route("/auth/verify-otp", methods=["POST"])
def verify_otp_route():
    data = request.get_json()
    return verif_otp(data.get("mobile"), data.get("otp"))


@app.route("/auth/forget-password", methods=["POST"])
def forget_password_route():
    data = request.get_json()
    return forget_password(data.get("mobile"))


@token_required
@app.route("/auth/change-password", methods=["POST"])
def change_password_route():
    data = request.get_json()
    return change_password(data.get("mobile"), data.get("password"))


@app.route("/user/me", methods=["GET"])
@token_required
def user_details_route(current_user):
    return user_details(current_user)


@app.route("/chatroom", methods=["POST"])
@token_required
def create_chatroom_route(current_user):
    return create_chatroom(current_user)


@app.route("/chatroom", methods=["GET"])
@token_required
def get_all_chatrooms_route(current_user):
    print("reched here with the current user: ", current_user)
    return get_all_chatrooms(current_user)


@app.route("/chatroom/<uuid:chatroom_id>", methods=["GET"])
@token_required
def get_chatroom_details_route(current_user, chatroom_id):
    return get_chatroom_details(current_user, chatroom_id)


@app.route("/subscription/pro", methods=["POST"])
@token_required
def pro_subscription(current_user):
    return create_pro_subscription(current_user)


@app.route("/webhook/stripe", methods=["POST"])
def stripe_webhook_route():
    return stripe_webhook(request)


@app.route("/subscription/status", methods=["GET"])
@token_required
def subscription_status(current_user):
    return get_subscription_status(current_user)


@app.route("/chatroom/<uuid:chatroom_id>/message", methods=["POST"])
@token_required
def message_route(current_user, chatroom_id):
    data = request.get_json()
    return generate_message(current_user, chatroom_id)

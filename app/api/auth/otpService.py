import random
import jwt
import app.utils.redis_client as redis_client


from app.api.auth.helpers import generate_salt, hash_password
from datetime import datetime, timezone, timedelta
from app.db.models import User, db
from app.utils.redis_client import RedisClient
from app.utils.redis_keys import mobile_otp_key
from flask import current_app, jsonify

redis_client = RedisClient()  # noqa: F811


# auth/send-otp
def send_otp(mobile):
    print("here is the mobile number: ", mobile)
    otp = random.randint(1000, 9999)

    # 5 minutes of expiry
    redis_client.setex(mobile_otp_key(mobile), 300, otp)
    return jsonify({"status": True, "message": f"{otp}"}), 200


# auth/verify-otp
def verif_otp(mobile, otp):
    stored_otp_bytes = redis_client.get(mobile_otp_key(mobile))

    if stored_otp_bytes is None:
        return jsonify(
            {
                "status": False,
                "message": "OTP has expired",
            }
        ), 400

    stored_otp = stored_otp_bytes.decode("utf-8")
    if otp != stored_otp:
        return jsonify(
            {
                "status": False,
                "message": "OTP does not match",
            }
        )

    else:
        user = User.query.filter_by(mobile=mobile).first()

        if not user:
            return jsonify(
                {
                    "status": False,
                    "message": "User does not exist, signup first",
                }
            ), 404

        payload = {
            "sub": str(user.userid),
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(days=7),
        }

        try:
            token = jwt.encode(
                payload=payload, key=current_app.config["SECRET_KEY"], algorithm="HS256"
            )
        except Exception as e:
            print("[Error] error while generating token: ", e)
            return jsonify({"status": False, "message": "internal server error"}), 500

        redis_client.delete(mobile_otp_key(mobile))
        return jsonify(
            {
                "status": True,
                "message": "OTP verified",
                "token": token,
            }
        ), 200


def forget_password(mobile):
    otp = random.randint(1000, 9999)

    # 5 minutes of expiry
    redis_client.setex(mobile_otp_key(mobile), 300, otp)
    return jsonify({"status": True, "message": f"{otp}"}), 200


def change_password(mobile, new_password):
    try:
        user = User.query.filter_by(mobile=mobile).first()

        if not user:
            return jsonify(
                {
                    "status": False,
                    "message": "User does not exist, signup first",
                }
            ), 404

        salt = generate_salt()

        hashed_password = hash_password(new_password, salt)
        user.password = hashed_password
        user.salt = salt

        db.session.commit()

        return jsonify(
            {"status": True, "message": "Password changed successfully"}
        ), 200
    except Exception as e:
        print("[Error] error while changing password: ", e)
        db.session.rollback()
        return jsonify({"status": False, "message": "internal server error"}), 500

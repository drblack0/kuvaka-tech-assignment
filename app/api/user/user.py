from flask import jsonify


def user_details(current_user):
    user = {
        "userid": current_user.userid,
        "mobile": current_user.mobile,
        "username": current_user.username,
    }
    
    return jsonify({"status": True, "user": user}), 200

from flask import request, jsonify
from app.db.models import db, Chatroom, Message
from celery_worker import process_gemini_request  # <-- IMPORT YOUR CELERY TASK


def generate_message(current_user, chatroom_id):
    """
    Receives a user message, saves it, and dispatches a task to the Gemini API.
    """
    data = request.get_json()
    user_message_content = data.get("content")

    if not user_message_content:
        return jsonify({"status": False, "message": "Message content is required"}), 400

    try:
        # 1. Verify the chatroom exists and belongs to the user
        chatroom = Chatroom.query.filter_by(
            id=chatroom_id, user_id=current_user.userid
        ).first()
        if not chatroom:
            return jsonify({"status": False, "message": "Chatroom not found"}), 404

        # 2. Save the user's message to the database IMMEDIATELY
        user_message = Message(
            content=user_message_content, sender="user", chatroom_id=chatroom_id
        )
        db.session.add(user_message)
        db.session.commit()

        # 3. Dispatch the background task to Celery
        # We pass primitive types (strings) to the task
        process_gemini_request.delay(user_message_content, str(chatroom_id))

        # 4. Return an immediate response to the client
        return jsonify(
            {"status": True, "message": "Message received and is being processed"}
        ), 202  # 202 Accepted is the correct status code for async processing

    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] in post_message: {e}")
        return jsonify({"status": False, "message": "Internal server error"}), 500

import json
from flask import request, jsonify
from app.db.models import db, Chatroom, Message  # Import the new models
from app.utils.redis_client import RedisClient
from app.utils.redis_keys import chatroom_key

redisClient = RedisClient()


def create_chatroom(current_user):
    """Creates a new chatroom for the authenticated user."""
    data = request.get_json()
    title = data.get("title", "New Chat")  # Use a provided title or a default
    cache_key = chatroom_key(current_user.userid)

    try:
        new_chatroom = Chatroom(title=title, user_id=current_user.userid)
        db.session.add(new_chatroom)
        db.session.commit()
        redisClient.delete(cache_key)

        return jsonify(
            {
                "status": True,
                "message": "Chatroom created successfully",
                "chatroom": {
                    "id": str(new_chatroom.id),
                    "title": new_chatroom.title,
                    "created_at": new_chatroom.created_at,
                },
            }
        ), 201
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] in create_chatroom: {e}")
        return jsonify({"status": False, "message": "Internal server error"}), 500


def get_all_chatrooms(current_user):
    """Lists all chatrooms for the user, with caching."""

    cache_key = chatroom_key(current_user.userid)

    try:
        cached_chatrooms = redisClient.get(cache_key)
        if cached_chatrooms:
            return jsonify(
                {
                    "status": True,
                    "source": "cache",
                    "chatrooms": json.loads(
                        cached_chatrooms
                    ),  # Decode JSON string from cache
                }
            ), 200

        # 3. Cache Miss: Query the database
        chatrooms = (
            Chatroom.query.filter_by(user_id=current_user.userid)
            .order_by(Chatroom.created_at.desc())
            .all()
        )

        chatrooms_list = [
            {"id": str(c.id), "title": c.title, "created_at": c.created_at.isoformat()}
            for c in chatrooms
        ]

        # 4. Store the result in Redis with a 5-minute TTL (300 seconds)
        redisClient.setex(cache_key, 300, json.dumps(chatrooms_list))

        return jsonify(
            {"status": True, "source": "database", "chatrooms": chatrooms_list}
        ), 200

    except Exception as e:
        print(f"[ERROR] in get_all_chatrooms: {e}")
        return jsonify({"status": False, "message": "Internal server error"}), 500


def get_chatroom_details(current_user, chatroom_id):
    try:
        chatroom = Chatroom.query.get(chatroom_id)

        if not chatroom or chatroom.user_id != current_user.userid:
            return jsonify({"status": False, "message": "Chatroom not found"}), 404

        # Query messages for this chatroom, ordered by creation time
        messages = (
            Message.query.filter_by(chatroom_id=chatroom.id)
            .order_by(Message.created_at.asc())
            .all()
        )

        messages_list = [
            {
                "id": str(m.id),
                "content": m.content,
                "sender": m.sender,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ]

        return jsonify(
            {
                "status": True,
                "chatroom": {
                    "id": str(chatroom.id),
                    "title": chatroom.title,
                    "created_at": chatroom.created_at.isoformat(),
                    "messages": messages_list,
                },
            }
        ), 200

    except Exception as e:
        print(f"[ERROR] in get_chatroom_details: {e}")
        return jsonify({"status": False, "message": "Internal server error"}), 500

import datetime
import uuid
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

from sqlalchemy import UUID

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    userid = db.Column(db.String, primary_key=True, default=lambda: str(uuid4()))
    mobile = db.Column(db.String(15), unique=True, nullable=False)
    username = db.Column(db.String(50), nullable=True)  # Added username
    password = db.Column(db.String(128), nullable=False)  # This will store the HASH
    salt = db.Column(db.String(64), nullable=False)

    subscription_tier = db.Column(db.String(20), nullable=False, default="basic")
    stripe_customer_id = db.Column(db.String(128), unique=True, nullable=True)

    def __repr__(self):
        return f"<User {self.username} ({self.mobile})>"


class Chatroom(db.Model):
    __tablename__ = "chatrooms"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(100), nullable=False, default="New Chat")
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Foreign Key to link to the user
    user_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("users.userid"), nullable=False
    )

    # This creates a back-reference so you can access chatroom.messages
    messages = db.relationship(
        "Message", backref="chatroom", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Chatroom {self.id}>"


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # 'user' or 'ai'
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Foreign Key to link to the chatroom
    chatroom_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("chatrooms.id"), nullable=False
    )

    def __repr__(self):
        return f"<Message from {self.sender}>"

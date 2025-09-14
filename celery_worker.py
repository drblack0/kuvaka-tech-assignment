import os
from celery import Celery
from flask import Flask
from dotenv import load_dotenv
from google import genai
from app.db.models import db

load_dotenv()


def create_flask_app():
    app = Flask(__name__)
    print(os.environ.get("SQLALCHEMY_DATABASE_URI"))
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    return app


rabbit_url = os.environ.get("RABBIT_URL")
gemini_api_key = os.environ.get("GEMINI_API_KEY")

celery_app = Celery("tasks", broker=rabbit_url)

client = genai.Client(api_key=gemini_api_key)

# response = client.models.generate_content(
#     model="gemini-2.5-flash", contents="Explain how AI works in a few words"
# )
# print(response.text)


@celery_app.task
def process_gemini_request(user_message_content, chatroom_id):
    """
    This is the background task that calls the Gemini API and saves the response.
    """
    # Create a Flask app context so we can use SQLAlchemy
    print("inside the celery worker")
    app = create_flask_app()
    with app.app_context():
        from app.db.models import db, Message  # Import models inside the context

        try:
            # 1. Call the Google Gemini API
            print(
                f"Sending to Gemini: '{user_message_content}' for chatroom {chatroom_id}"
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=user_message_content
            )
            ai_message_content = response.text
            print(f"Received from Gemini: '{ai_message_content}'")

            ai_message = Message(
                content=ai_message_content, sender="ai", chatroom_id=chatroom_id
            )

            # 3. Save the AI's response to the database
            db.session.add(ai_message)
            db.session.commit()
            print(f"Successfully saved AI message to chatroom {chatroom_id}")

        except Exception as e:
            # Handle potential errors from the API call or database write
            print(
                f"[CELERY_WORKER_ERROR] Failed to process message for chatroom {chatroom_id}: {e}"
            )
            # You might want to implement a retry mechanism here

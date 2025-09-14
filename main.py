import os
from re import L
from flask import Flask, jsonify
from sqlalchemy import inspect, text

from app.middleware.auth import token_required
from app.routes import app
from dotenv import load_dotenv
from app.db.models import db

load_dotenv()

db.init_app(app)


@app.route("/")
def hello_world():
    print("hello world")
    return "<p>Hello, World!</p>"


@token_required
@app.route("/test")
def test():
    print("test")
    return "<p>test</p>"


@app.route("/debug-db")
def debug_db_connection():
    try:
        # Log the DATABASE_URL the app is actually using.
        db_url = os.environ.get("DATABASE_URL")
        print(f"DEBUG: Connecting to DATABASE_URL: {db_url}")

        # Use SQLAlchemy's inspector to get table names from the live connection.
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        print(f"DEBUG: Found tables: {tables}")

        # Return the information as a JSON response.
        return {
            "status": "success",
            "database_url_used": db_url,
            "tables_found": tables,
        }
    except Exception as e:
        print(f"DEBUG: Error during database inspection: {e}")
        return {"status": "error", "message": str(e)}, 500


if __name__ == "__main__":
    app.run()

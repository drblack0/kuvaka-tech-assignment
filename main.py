import os
from re import L
from flask import Flask, jsonify
from sqlalchemy import text

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

if __name__ == "__main__":
    app.run()

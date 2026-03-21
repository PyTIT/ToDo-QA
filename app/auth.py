import re

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db
from .models import User

auth_bp = Blueprint("auth", __name__)

CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")
LATIN_RE = re.compile(r"[A-Za-z]")
DIGIT_RE = re.compile(r"\d")


def has_whitespace(value: str) -> bool:
    return any(char.isspace() for char in value)


def validate_username(username: str) -> str | None:
    if not username:
        return "Username is required"

    if username.strip() == "":
        return "Username is required"

    if has_whitespace(username):
        return "Username must not contain spaces"

    if len(username) < 3 or len(username) > 30:
        return "Username must be from 3 to 30 characters"

    if CYRILLIC_RE.search(username):
        return "Username must not contain Cyrillic characters"

    if username.isdigit():
        return "Username must not contain only digits"

    return None


def validate_password(password: str) -> str | None:
    if not password:
        return "Password is required"

    if has_whitespace(password):
        return "Password must not contain spaces"

    if len(password) < 8 or len(password) > 32:
        return "Password must be from 8 to 32 characters"

    if CYRILLIC_RE.search(password):
        return "Password must not contain Cyrillic characters"

    if not LATIN_RE.search(password):
        return "Password must contain at least one Latin letter"

    if not DIGIT_RE.search(password):
        return "Password must contain at least one digit"

    return None


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}

    username = data.get("username") or ""
    password = data.get("password") or ""

    username_error = validate_username(username)
    if username_error:
        return jsonify({"message": username_error}), 400

    password_error = validate_password(password)
    if password_error:
        return jsonify({"message": password_error}), 400

    normalized_username = username.strip()

    existing_user = User.query.filter_by(username=normalized_username).first()
    if existing_user:
        return jsonify({"message": "Username already exists"}), 409

    user = User(
        username=normalized_username,
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    username = data.get("username") or ""
    password = data.get("password") or ""

    username_error = validate_username(username)
    if username_error:
        return jsonify({"message": username_error}), 400

    password_error = validate_password(password)
    if password_error:
        return jsonify({"message": password_error}), 400

    normalized_username = username.strip()

    user = User.query.filter_by(username=normalized_username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid username or password"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": access_token}), 200
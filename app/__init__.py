from flask import Flask, render_template

from .config import Config
from .extensions import db, jwt
from .auth import auth_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(auth_bp)

    @app.get("/")
    def index():
        return render_template("index.html")

    return app
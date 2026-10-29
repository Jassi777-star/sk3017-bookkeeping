import os
from pathlib import Path

from flask import Flask, redirect, render_template, send_from_directory, url_for
from dotenv import load_dotenv

from app.extensions import csrf, db


def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "DATABASE_URL",
            "sqlite:///bookkeeping.sqlite",
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True},
    )

    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    csrf.init_app(app)

    from app.routes.categories import categories_bp
    from app.routes.budget import budget_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.entries import entries_bp

    app.register_blueprint(categories_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(entries_bp)

    from app.cli import register_commands

    register_commands(app)

    @app.get("/")
    def index():
        return redirect(url_for("dashboard.dashboard"))

    @app.get("/favicon.ico")
    def favicon():
        return send_from_directory(
            app.static_folder,
            "favicon.svg",
            mimetype="image/svg+xml",
        )

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(_error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    return app

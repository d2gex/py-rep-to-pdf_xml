from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from src import config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=config.Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    # require to import models here so that migrate knows what to generate
    from src import models
    migrate.init_app(app, db)

    # Add apis's blueprint
    from src.apis.handler import api_v1
    app.register_blueprint(api_v1, url_prefix='/api')

    return app

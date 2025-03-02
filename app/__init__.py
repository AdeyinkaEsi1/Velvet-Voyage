from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, static_folder="static")
    from config import Config
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Import Blueprints only once and with unique names
    from app.routes.flights import bp as flights_bp
    from app.routes.booking import bp as booking_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.main import bp as main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(flights_bp, url_prefix='/flights')
    app.register_blueprint(booking_bp, url_prefix='/booking')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    return app
    

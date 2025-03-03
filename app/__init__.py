from flask import Flask
import mysql.connector


def create_app():
    app = Flask(__name__, static_folder="static")
    from config import Config
    app.config.from_object(Config)

    db = mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )
    
    # Import Blueprints only once and with unique names
    from app.routes.flights import bp as flights_bp
    from app.routes.booking import bp as booking_bp
    from app.routes.signup import bp as signup_bp
    from app.routes.flight_price import bp as flight_price_bp
    from app.routes.login import bp as login_bp
    from app.routes.main import bp as main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(flights_bp, url_prefix='/flights')
    app.register_blueprint(booking_bp, url_prefix='/booking')
    app.register_blueprint(signup_bp, url_prefix='/signup')
    app.register_blueprint(flight_price_bp, url_prefix='/flight_price')
    app.register_blueprint(login_bp, url_prefix='/login')
    
    
    return app
    

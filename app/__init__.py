from flask import Flask, jsonify, redirect, render_template, url_for
from flask_jwt_extended import JWTManager
import mysql.connector
from datetime import timedelta
from secret import jwt_key, secret_key
from flask_mail import Mail

def create_app():
    app = Flask(__name__, static_folder="static")
    from config import Config
    app.config.from_object(Config)
    app.config["SECRET_KEY"] = secret_key
    app.config["JWT_SECRET_KEY"] = jwt_key
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=3)
    
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token_cookie"
    app.config["JWT_COOKIE_SECURE"] = False
    app.config["JWT_COOKIE_HTTPONLY"] = True
    app.config["JWT_COOKIE_SAMESITE"] = "Lax"
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    jwt = JWTManager(app)
    global mail
    mail = Mail()
    mail.init_app(app)
    
    # Blocklist storage
    global revoked_tokens
    revoked_tokens = set()
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return redirect(url_for('auth.login_page', message="Session expired. Please log in again."))
    
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return redirect(url_for('auth.login_page', message="You have to log in"))


    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload):
        return jwt_payload["jti"] in revoked_tokens

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404
    
    # Import Blueprints
    from app.routes.booking import bp as booking_bp
    from app.routes.flight_book import bp as flight_book_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.logout import bp as logout_bp
    from app.routes.main import bp as main_bp
    from app.routes.user import bp as user_bp
    from app.routes.admin import bp as admin_bp
    from app.routes.payment import bp as payment_bp
    from app.routes.dashboard import bp as dashboard_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(booking_bp, url_prefix='/bookings')
    app.register_blueprint(flight_book_bp, url_prefix='/flight_book')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(logout_bp, url_prefix='/logout')
    app.register_blueprint(payment_bp, url_prefix='/payment')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    
    
    return app
    

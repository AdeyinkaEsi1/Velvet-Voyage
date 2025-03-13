from datetime import timedelta, timezone
from flask import Blueprint, request, jsonify, render_template, make_response
import mysql.connector
from flask_bcrypt import Bcrypt
from flask_jwt_extended import get_jwt_identity, jwt_required, create_access_token, verify_jwt_in_request, get_jwt
from config import Config
import re
import random
from flask_mail import Mail, Message
from datetime import datetime
from app import mail


bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()


def get_db_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )
    
    
@bp.route('/register', methods=['POST'])
def register():
    data = request.json
    required_fields = ["first_name", "last_name", "email", "confirm_email", "address", "city", 
                       "mobile_number", "date_of_birth", "gender", "password", "confirm_password"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "All fields are required"}), 400

    first_name = data["first_name"].strip().title()
    last_name = data["last_name"].strip().title()
    email = data["email"].strip().lower()
    confirm_email = data["confirm_email"].strip().lower()
    address = data["address"].strip()
    city = data["city"].strip().title()
    mobile_number = data["mobile_number"].strip()
    date_of_birth = data["date_of_birth"]
    gender = data["gender"]
    password = data["password"]
    confirm_password = data["confirm_password"]
    
    # Validate email
    if email != confirm_email:
        return jsonify({"error": "Emails do not match"}), 400
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"error": "Invalid email format"}), 400

    # Validate password
    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    
        # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
                       INSERT INTO users (first_name, last_name, email, address, city, mobile_number, 
                            date_of_birth, gender, password_hash)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (first_name, last_name, email, address, city, mobile_number, date_of_birth, gender, hashed_password))
    
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409
    finally:
        cursor.close()
        conn.close()    


@bp.route('/login_page', methods=['GET'])
def login_page():
    message = request.args.get('message')
    return render_template('user/auth/login.html', message=message)

@bp.route('/register_page', methods=['GET'])
def register_page():
    return render_template('user/auth/register.html')


@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', "").strip().lower()
    password = data.get('password', "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user and bcrypt.check_password_hash(user['password_hash'], password):
        access_token = create_access_token(identity=str(user['id']))

        response = make_response(jsonify({"message": "Login successful"}))
        response.set_cookie(
        "access_token_cookie", access_token,
        httponly=True, secure=False, samesite="Lax"
        )
        return response, 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401     

    

@bp.route('/is_authenticated', methods=['GET'])
@jwt_required()
def is_authenticated():
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        jwt_data = get_jwt()

        exp_timestamp = jwt_data.get("exp", 0)
        if datetime.fromtimestamp(exp_timestamp, timezone.utc) < datetime.now(timezone.utc):
            return jsonify({"error": "Token expired"}), 401

        return jsonify({"message": "User is authenticated", "user_id": user_id}), 200
    except Exception as e:
        return jsonify({"error": "Not authenticated", "details": str(e)}), 401


@bp.route('/password-reset', methods=['GET'])
def password_reset_page():
    return render_template('user/auth/password-reset.html')



@bp.route('/password-reset/request', methods=['POST'])
def request_password_reset():
    data = request.json
    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({"error": "Email is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    
    if not user:
        return jsonify({"error": "User not found"}), 404

    otp = str(random.randint(100000, 999999))
    otp_expiry = datetime.utcnow() + timedelta(minutes=10)
    
    cursor.execute("UPDATE users SET reset_otp = %s, otp_expires = %s WHERE email = %s",
                   (otp, otp_expiry, email))
    conn.commit()

    msg = Message(
    subject="HT Travels Password Reset Code",
    recipients=[email]
    )

    first_name = user.get("first_name", "Valued Customer")

    msg.body = f"""
    Hello {first_name},

    Your HT Travels password reset code is: {otp}

    This OTP is valid for 10 minutes. If you didn't request this, please ignore this email.

    Best regards,  
    HT Travels Team
    """

    msg.html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #2E86C1;">HT Travels Password Reset</h2>
            <p>Hello <strong style="color: blue;">{first_name}</strong>,</p>
            <p>Your password reset OTP is: <strong style="font-size: 18px;">{otp}</strong></p>
            <p>This OTP is valid for <strong>10 minutes</strong>. If you didn't request this, please ignore this email.</p>
            <br>
            <p>Best regards,<br>HT Travels Team</p>
        </body>
    </html>
    """

    mail.send(msg)

    return jsonify({"message": "OTP sent to email"}), 200



@bp.route('/password-reset/verify', methods=['POST'])
def verify_otp_and_reset_password():
    data = request.json
    email = data.get("email", "").strip().lower()
    otp = data.get("otp", "")
    new_password = data.get("new_password", "")

    if not all([email, otp, new_password]):
        return jsonify({"error": "All fields are required"}), 400
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if not user or user["reset_otp"] != otp:
        return jsonify({"error": "Invalid OTP"}), 400
    
    if datetime.utcnow() > user["otp_expires"]:
        return jsonify({"error": "OTP expired"}), 400

    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    cursor.execute("UPDATE users SET password_hash = %s, reset_otp = NULL, otp_expires = NULL WHERE email = %s",
                   (hashed_password, email))
    conn.commit()

    return jsonify({"message": "Password successfully reset"}), 200



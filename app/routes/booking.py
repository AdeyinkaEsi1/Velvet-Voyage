from flask import Blueprint, request, jsonify, render_template
import mysql.connector
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import Config
import uuid

bp = Blueprint('bookings', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )

@bp.route('/book', methods=["POST"])
@jwt_required()
def book_flight():
    print("Cookies received:", request.cookies)
    user_id = get_jwt_identity()
    print("User ID extracted:", user_id)
    data = request.json
    
    required_fields = ["flight_id", "seats", "flight_class", "round_trip"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "All fields are required"}), 400

    flight_id = data["flight_id"]
    seats = data["seats"]
    flight_class = data["flight_class"].lower()
    round_trip = data["round_trip"]

    # Input Validation
    if seats < 1 or seats > 130:
        return jsonify({"error": "Seats must be between 1 and 130"}), 400
    if flight_class not in ["economy", "business", "premium"]:
        return jsonify({"error": "Invalid flight class"}), 400
    

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        booking_id = str(uuid.uuid4())[:12].replace("-", "").upper()
        
        cursor.execute("""
            INSERT INTO bookings (booking_id, user_id, flight_id, booking_time, seats, flight_class, round_trip)
            VALUES (%s, %s, %s, NOW(), %s, %s, %s)
        """, (booking_id, user_id, flight_id, seats, flight_class, round_trip))
        conn.commit()
        
        booking_id = cursor.lastrowid
        cursor.execute("SELECT * FROM bookings WHERE id = %s", (booking_id,))
        booking_details = cursor.fetchone()

        return jsonify({
            "message": "Successfully booked a flight",
            "booking": {
                "user_id": booking_details[1],
                "flight_id": booking_details[2],
                "booking_time": str(booking_details[3]),
                "seats": booking_details[4],
                "flight_class": booking_details[5],
                "round_trip": bool(booking_details[6]),
                "booking_id": booking_details[7],
            }
        }), 200
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {str(err)}"}), 500
    finally:
        cursor.close()
        conn.close()
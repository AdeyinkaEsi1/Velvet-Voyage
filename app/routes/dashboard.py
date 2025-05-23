from flask import flash
from flask import Blueprint, jsonify, render_template, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import mysql.connector
from datetime import datetime, timedelta
from config import Config
from werkzeug.security import check_password_hash

bp = Blueprint('dashboard', __name__)



def get_db_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )



@bp.route('/profile', methods=['GET', 'POST'])
@jwt_required()
def user_profile():
    user_id = get_jwt_identity()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        data = request.form
        
        current_password = data.get("current_password")
        new_password = data.get("password")
        confirm_password = data.get("confirm_password")
        
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()

        if not user_data:
            return "User not found", 404
        
        if not user_data.get("password_hash"):
            flash("Password data is missing. Please reset your password.", "error")
        elif not check_password_hash(user_data["password_hash"], current_password):
            flash("Current password is incorrect.", "error")

        else:
            cursor.execute("""
                UPDATE users
                SET first_name = %s, last_name = %s, email = %s, address = %s, city = %s, 
                    mobile_number = %s, date_of_birth = %s, gender = %s, password = %s
                WHERE id = %s
            """, (
                data.get("first_name"),
                data.get("last_name"),
                data.get("email"),
                data.get("address"),
                data.get("city"),
                data.get("mobile_number"),
                data.get("date_of_birth"),
                data.get("gender"),
                data.get("password"),
                user_id
            ))

            conn.commit()
            flash("Profile updated successfully!", "success")

    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user_data:
        return "User not found", 404

    return render_template("user/dashboard/profile.html", data=user_data)



@bp.route('/generate_receipt', methods=['GET'])
@jwt_required()
def generate_receipt():
    return render_template("user/dashboard/generate_receipt.html")


@bp.route('/bookings', methods=['GET'])
@jwt_required()
def user_bookings():
    user_id = get_jwt_identity()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT b.booking_id, b.flight_id, f.departure, f.destination, f.departure_time, 
           f.arrival_time, b.seats, b.flight_class, b.round_trip, b.status, b.booking_time, 
           b.payment_reference, b.total_price
    FROM bookings b
    LEFT JOIN flights f ON b.flight_id = f.id
    WHERE b.user_id = %s
    ORDER BY b.booking_time DESC
    """
    
    cursor.execute(query, (user_id,))
    bookings = cursor.fetchall()
    
    for booking in bookings:
        if isinstance(booking["departure_time"], timedelta):
            booking["departure_time"] = str(booking["departure_time"])
        if isinstance(booking["arrival_time"], timedelta):
            booking["arrival_time"] = str(booking["arrival_time"])

    cursor.close()
    conn.close()

    return render_template("user/dashboard/bookings.html", bookings=bookings)
    # return jsonify({"bookings": bookings}), 200



@bp.route('/cancel', methods=['PUT'])
@jwt_required()
def cancel_booking():
    user_id = get_jwt_identity()
    data = request.json
    booking_id = data.get("booking_id")

    if not booking_id:
        return jsonify({"error": "Booking ID is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT departure_time, total_price, status FROM bookings 
        WHERE booking_id = %s AND user_id = %s
    """, (booking_id, user_id))
    
    booking = cursor.fetchone()

    if not booking:
        return jsonify({"error": "Booking not found or not authorized"}), 404

    if booking["status"] in ("completed", "checked-in", "cancelled"):
        return jsonify({"error": f"Booking cannot be cancelled (current status: {booking['status']})"}), 400

    departure_time = (datetime.min + booking["departure_time"]).time()  # Convert timedelta to time
    departure_datetime = datetime.combine(datetime.now().date(), departure_time)
    cancel_date = datetime.now()
    days_before_departure = (departure_datetime - cancel_date).days


    cancellation_fee = 0
    if 30 <= days_before_departure < 60:
        cancellation_fee = 0.40 * booking["total_price"]
    elif days_before_departure < 30:
        cancellation_fee = booking["total_price"]

    cursor.execute("""
        UPDATE bookings 
        SET status = 'cancelled', cancellation_fee = %s
        WHERE booking_id = %s
    """, (cancellation_fee, booking_id))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "message": "Booking cancelled",
        "cancellation_fee": cancellation_fee
    }), 200


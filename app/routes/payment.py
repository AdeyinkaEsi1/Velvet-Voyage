from datetime import datetime, timedelta
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import mysql.connector
import random, string
from config import Config



bp = Blueprint('payment', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )


@bp.route('/', methods=["GET"])
@jwt_required()
def payment_page():
    user_id = get_jwt_identity()
    
    flight_id = request.args.get("flightId")
    print(flight_id)
    departure = request.args.get("departure")
    print(departure)
    destination = request.args.get("destination")
    print(destination)
    departure_time = request.args.get("departure_time")
    arrival_time = request.args.get("arrival_time")
    seats = request.args.get("seats")
    flight_class = request.args.get("flight_class")
    round_trip = request.args.get("round_trip")
    base_price = request.args.get("base_price")
    discount = request.args.get("discount")
    final_price = request.args.get("final_price")

    print("DEBUG: Received Query Parameters:", request.args)
    if not flight_id or not departure:
        return render_template("payment.html", error="Invalid booking details"), 400
    
    return render_template(
            "payment.html",
            user_id = user_id,
            flight_id=flight_id,
            departure=departure,
            destination=destination,
            departure_time=departure_time,
            arrival_time=arrival_time,
            seats=seats,
            flight_class=flight_class,
            round_trip=round_trip,
            base_price=base_price,
            discount=discount,
            final_price=final_price,
        )


@bp.route('/<booking_id>', methods=['GET'])
@jwt_required()
def payment_details_page(booking_id):
    user_id = get_jwt_identity()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT b.*, f.departure, f.destination, f.departure_time, f.arrival_time
        FROM bookings b
        JOIN flights f ON b.flight_id = f.id
        WHERE b.booking_id = %s AND b.user_id = %s
    """, (booking_id, user_id))
    booking = cursor.fetchone()

    cursor.close()
    conn.close()

    if not booking:
        return "Booking not found", 404

    return render_template(
        "payment.html",
        booking_id=booking["booking_id"],
        flight_id=booking["flight_id"],
        departure=booking["departure"],
        destination=booking["destination"],
        departure_time=booking["departure_time"],
        arrival_time=booking["arrival_time"],
        seats=booking["seats"],
        flight_class=booking["flight_class"],
        round_trip="Yes" if booking["round_trip"] else "No",
        base_price=booking["total_price"] + booking["discount_applied"],
        discount=booking["discount_applied"],
        final_price=booking["total_price"],
    )



@bp.route('/pay', methods=['POST'])
@jwt_required()
def process_payment():
    user_id = get_jwt_identity()
    booking_id = request.form.get("booking_id")
    card_number = request.form.get("card_number")
    expiry = request.form.get("expiry")
    cvv = request.form.get("cvv")

    if not booking_id or not card_number or not expiry or not cvv:
        return jsonify({"error": "All payment details are required"}), 400

    # Simulated card validation
    if len(card_number) < 16 or len(cvv) < 3:
        return jsonify({"error": "Invalid card details"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT status, payment_status FROM bookings WHERE booking_id = %s AND user_id = %s", 
                   (booking_id, user_id))
    booking = cursor.fetchone()

    if not booking:
        return jsonify({"error": "Booking not found or not authorized"}), 404
    payment_reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

    cursor.execute("""
        UPDATE bookings 
        SET payment_status = 'paid', status = 'confirmed', payment_reference = %s 
        WHERE booking_id = %s
    """, (payment_reference, booking_id))
    conn.commit()
    
    cursor.close()
    conn.close()

    return redirect(url_for('dashboard.user_bookings'))


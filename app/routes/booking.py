from datetime import timedelta
from flask import Blueprint, request, jsonify, render_template, Response
import mysql.connector
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import Config
import uuid
import random
import string
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from datetime import datetime


bp = Blueprint('bookings', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )

        


@bp.route('/', methods=['GET'])
@jwt_required()
def get_user_bookings():
    user_id = get_jwt_identity()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT b.booking_id, b.flight_id, f.departure, f.destination, f.departure_time, 
           f.arrival_time, b.seats, b.flight_class, b.round_trip, b.status, b.booking_time, b.payment_reference
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

    return jsonify({"bookings": bookings}), 200


@bp.route('/book', methods=["POST"])
@jwt_required()
def book_flight():
    user_id = get_jwt_identity()
    data = request.json
    
    required_fields = ["flight_id", "seats", "flight_class", "round_trip"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "All fields are required"}), 400

    flight_id = data["flight_id"]
    seats = data["seats"]
    flight_class = data["flight_class"].lower()
    round_trip = data["round_trip"]

    if seats < 1 or seats > 130:
        return jsonify({"error": "Seats must be between 1 and 130"}), 400
    if flight_class not in ["economy", "business", "premium"]:
        return jsonify({"error": "Invalid flight class"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT f.departure, f.destination, f.departure_time, fp.price
        FROM flights f
        JOIN flight_prices fp ON f.departure = fp.departure AND f.destination = fp.destination
        WHERE f.id = %s
    """, (flight_id,))
    
    flight = cursor.fetchone()

    if not flight:
        return jsonify({"error": "Flight not found"}), 404

    departure_time = (datetime.min + flight["departure_time"]).time()  # Convert timedelta to time
    departure_datetime = datetime.combine(datetime.now().date(), departure_time)
    booking_date = datetime.now()
    days_in_advance = (departure_datetime - booking_date).days

    discount_percentage = 0
    if 80 <= days_in_advance <= 90:
        discount_percentage = 25
    elif 60 <= days_in_advance <= 79:
        discount_percentage = 15
    elif 45 <= days_in_advance <= 59:
        discount_percentage = 10

    original_price = flight["price"] * seats
    discount_amount = (discount_percentage / 100) * original_price
    final_price = original_price - discount_amount

    booking_id = str(uuid.uuid4())[:12].replace("-", "").upper()
    
    cursor.execute("""
        INSERT INTO bookings (booking_id, user_id, flight_id, booking_time, seats, flight_class, 
                              round_trip, status, total_price, discount_applied)
        VALUES (%s, %s, %s, NOW(), %s, %s, %s, 'pending', %s, %s)
    """, (booking_id, user_id, flight_id, seats, flight_class, round_trip, final_price, discount_amount))

    conn.commit()
    
    cursor.execute("SELECT * FROM bookings WHERE booking_id = %s", (booking_id,))
    booking_details = cursor.fetchone()

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Successfully booked a flight",
        "booking": {
            "user_id": booking_details["user_id"],
            "flight_id": booking_details["flight_id"],
            "booking_time": str(booking_details["booking_time"]),
            "seats": booking_details["seats"],
            "flight_class": booking_details["flight_class"],
            "round_trip": bool(booking_details["round_trip"]),
            "booking_id": booking_details["booking_id"],
            "total_price": booking_details["total_price"],
            "discount_applied": booking_details["discount_applied"]
        }
    }), 200



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




@bp.route('/pay', methods=['POST'])
@jwt_required()
def process_payment():
    user_id = get_jwt_identity()
    data = request.json
    booking_id = data.get("booking_id")

    if not booking_id:
        return jsonify({"error": "Booking ID is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT status, payment_status FROM bookings WHERE booking_id = %s AND user_id = %s", 
                   (booking_id, user_id))
    booking = cursor.fetchone()

    if not booking:
        return jsonify({"error": "Booking not found or not authorized"}), 404

    if booking["status"] != "pending":
        return jsonify({"error": f"Booking cannot be paid for (current status: {booking['status']})"}), 400

    if booking["payment_status"] == "paid":
        return jsonify({"error": "Booking is already paid for"}), 400

    payment_successful = random.choice([True, False])  # Simulate success/failure

    if payment_successful:
        payment_reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))  # Generate ref
        cursor.execute("UPDATE bookings SET payment_status = 'paid', status = 'confirmed', payment_reference = %s WHERE booking_id = %s", 
                       (payment_reference, booking_id))
        conn.commit()

        return jsonify({"message": "Payment successful!", "payment_reference": payment_reference}), 200
    else:
        cursor.execute("UPDATE bookings SET payment_status = 'failed' WHERE booking_id = %s", (booking_id,))
        conn.commit()
        return jsonify({"error": "Payment failed. Try again."}), 400



@bp.route('receipt/<booking_id>', methods=['GET'])
@jwt_required()
def generate_receipt(booking_id):
    user_id = get_jwt_identity()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT b.booking_id, b.payment_status, b.payment_reference, f.departure, f.destination,
               f.departure_time, f.arrival_time, b.seats, b.flight_class, b.round_trip, b.status, b.booking_time
        FROM bookings b
        LEFT JOIN flights f ON b.flight_id = f.id
        WHERE b.booking_id = %s AND b.user_id = %s
    """, (booking_id, user_id))
    
    booking = cursor.fetchone()
    cursor.close()
    conn.close()

    if not booking:
        return jsonify({"error": "Booking not found or not authorized"}), 404

    if booking["payment_status"] != "paid":
        return jsonify({"error": "Receipt unavailable. Payment not completed."}), 400

    return jsonify({
        "receipt": {
            "booking_id": booking["booking_id"],
            "payment_reference": booking["payment_reference"],
            "flight": {
                "departure": booking["departure"],
                "destination": booking["destination"],
                "departure_time": str(booking["departure_time"]),
                "arrival_time": str(booking["arrival_time"])
            },
            "seats": booking["seats"],
            "class": booking["flight_class"],
            "round_trip": booking["round_trip"],
            "status": booking["status"],
            "booking_time": str(booking["booking_time"])
        }
    }), 200



@bp.route('/receipt/pdf/<booking_id>', methods=['GET'])
@jwt_required()
def generate_pdf_receipt(booking_id):
    user_id = get_jwt_identity()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT b.booking_id, b.payment_status, b.payment_reference, f.departure, f.destination,
               f.departure_time, f.arrival_time, b.seats, b.flight_class, b.round_trip, b.status, b.booking_time
        FROM bookings b
        LEFT JOIN flights f ON b.flight_id = f.id
        WHERE b.booking_id = %s AND b.user_id = %s
    """, (booking_id, user_id))
    
    booking = cursor.fetchone()
    cursor.close()
    conn.close()

    if not booking:
        return jsonify({"error": "Booking not found or not authorized"}), 404

    if booking["payment_status"] != "paid":
        return jsonify({"error": "Receipt unavailable. Payment not completed."}), 400

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle(f"Booking Receipt - {booking_id}")

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, 750, "Horizon Travels - Booking Receipt")
    
    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 720, f"Booking ID: {booking['booking_id']}")
    pdf.drawString(100, 700, f"Payment Reference: {booking['payment_reference']}")
    pdf.drawString(100, 680, f"Status: {booking['status'].capitalize()}")

    pdf.drawString(100, 650, f"Flight: {booking['departure']} → {booking['destination']}")
    pdf.drawString(100, 630, f"Departure Time: {str(booking['departure_time'])}")
    pdf.drawString(100, 610, f"Arrival Time: {str(booking['arrival_time'])}")

    pdf.drawString(100, 580, f"Seats: {booking['seats']}")
    pdf.drawString(100, 560, f"Class: {booking['flight_class'].capitalize()}")
    pdf.drawString(100, 540, f"Round Trip: {'Yes' if booking['round_trip'] else 'No'}")
    pdf.drawString(100, 520, f"Booking Time: {str(booking['booking_time'])}")

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    
    return Response(buffer, mimetype="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename=Horizon_Travels-receipt_{booking_id}.pdf'})



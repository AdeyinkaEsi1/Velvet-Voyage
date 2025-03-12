from datetime import timedelta
from flask import Blueprint, redirect, request, jsonify, render_template, Response, url_for
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
from flask import session


bp = Blueprint('bookings', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )


from flask_jwt_extended import jwt_required, get_jwt_identity



@bp.route('/confirm_booking', methods=['POST'])
@jwt_required()
def confirm_booking():
    user_id = get_jwt_identity() 

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    print("DEBUG: Received Data:", data)

    # Extract booking details
    flight_id = data.get("flight_id")
    seats = data.get("seats")
    flight_class = data.get("flight_class")
    round_trip = data.get("round_trip")
    base_price = data.get("base_price")
    discount = data.get("discount")
    final_price = data.get("final_price")

    print("DEBUG: Flight ID:", flight_id, "Type:", type(flight_id))

    if not all([flight_id, seats, flight_class, base_price, discount, final_price]):
        return jsonify({"error": "Missing booking details"}), 400

    try:
        flight_id = int(flight_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid flight_id: Must be an integer"}), 400

    if isinstance(round_trip, str):
        round_trip = round_trip.lower() == "true"
    round_trip = int(round_trip) 

    booking_id = str(uuid.uuid4())[:12].replace("-", "").upper()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id FROM flights WHERE id = %s", (flight_id,))
        flight = cursor.fetchone()

        if not flight:
            return jsonify({"error": f"Invalid flight_id: Flight {flight_id} does not exist"}), 400

        cursor.execute("""
            INSERT INTO bookings (booking_id, user_id, flight_id, booking_time, seats, flight_class, 
                                round_trip, status, total_price, discount_applied)
            VALUES (%s, %s, %s, NOW(), %s, %s, %s, 'pending', %s, %s)
        """, (booking_id, user_id, flight_id, seats, flight_class, round_trip, final_price, discount))

        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Failed to save booking", "details": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Booking confirmed!", "booking_id": booking_id}), 200





# @bp.route('/book', methods=["POST"])
# @jwt_required()
# def book_flight():
#     user_id = get_jwt_identity()
#     data = request.json
#     response_format = request.args.get("format", "json")
    
#     required_fields = ["flight_id", "seats", "flight_class", "round_trip"]
#     if not all(field in data for field in required_fields):
#         return jsonify({"error": "All fields are required"}), 400

#     flight_id = data["flight_id"]
#     seats = data["seats"]
#     flight_class = data["flight_class"].lower()
#     round_trip = data["round_trip"]

#     if seats < 1 or seats > 130:
#         return jsonify({"error": "Seats must be between 1 and 130"}), 400
#     if flight_class not in ["economy", "business", "premium"]:
#         return jsonify({"error": "Invalid flight class"}), 400
    
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     cursor.execute("""
#     SELECT f.id, f.departure, f.destination, f.departure_time, 
#            COALESCE(fp.price, dp.price) AS price
#     FROM flights f
#     LEFT JOIN flight_prices fp ON LOWER(TRIM(f.departure)) = LOWER(TRIM(fp.departure)) 
#                                AND LOWER(TRIM(f.destination)) = LOWER(TRIM(fp.destination))
#     LEFT JOIN flight_prices dp ON dp.departure = 'DEFAULT' AND dp.destination = 'DEFAULT'
#     WHERE f.id = %s
#     """, (flight_id,))
    
#     flight = cursor.fetchone()
#     print("DEBUG: Flight Query Result ->", flight)

#     if not flight:
#         if response_format == "json":
#             return jsonify({"error": "Flight not found"}), 404
#         else:
#             return redirect(url_for("main.home", error="Sorry, we have no flights available. Please edit your search to find other routes."))
        

#     departure_time = (datetime.min + flight["departure_time"]).time()  # Convert timedelta to time
#     departure_datetime = datetime.combine(datetime.now().date(), departure_time)
#     booking_date = datetime.now()
#     days_in_advance = (departure_datetime - booking_date).days

#     discount_percentage = 0
#     if 80 <= days_in_advance <= 90:
#         discount_percentage = 25
#     elif 60 <= days_in_advance <= 79:
#         discount_percentage = 15
#     elif 45 <= days_in_advance <= 59:
#         discount_percentage = 10

#     original_price = flight["price"] * seats
#     discount_amount = (discount_percentage / 100) * original_price
#     final_price = original_price - discount_amount

#     booking_id = str(uuid.uuid4())[:12].replace("-", "").upper()

#     cursor.execute("""
#         INSERT INTO bookings (booking_id, user_id, flight_id, booking_time, seats, flight_class, 
#                             round_trip, status, total_price, discount_applied)
#         VALUES (%s, %s, %s, NOW(), %s, %s, %s, 'pending', %s, %s)
#     """, (booking_id, user_id, flight_id, seats, flight_class, round_trip, final_price, discount_amount))

#     conn.commit()

#     cursor.execute("SELECT * FROM bookings WHERE booking_id = %s", (booking_id,))
#     booking_details = cursor.fetchone()

#     cursor.close()
#     conn.close()

#     print("DEBUG: Booking Details:", booking_details)

#     if not booking_details:
#         return jsonify({"error": "Booking not found"}), 404

#     if response_format == "json":
#         return jsonify({
#             "message": "Successfully booked a flight",
#             "booking": {
#                 "user_id": booking_details["user_id"],
#                 "flight_id": booking_details["flight_id"],
#                 "booking_time": str(booking_details["booking_time"]),
#                 "seats": booking_details["seats"],
#                 "flight_class": booking_details["flight_class"],
#                 "round_trip": bool(booking_details["round_trip"]),
#                 "booking_id": booking_details["booking_id"],
#                 "total_price": str(booking_details["total_price"]),
#                 "discount_applied": str(booking_details["discount_applied"])
#             }
#         }), 200
#     else:
#         return render_template("flight-book.html", booking=booking_details)



# @bp.route('/cancel', methods=['PUT'])
# @jwt_required()
# def cancel_booking():
#     user_id = get_jwt_identity()
#     data = request.json
#     booking_id = data.get("booking_id")

#     if not booking_id:
#         return jsonify({"error": "Booking ID is required"}), 400

#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     cursor.execute("""
#         SELECT departure_time, total_price, status FROM bookings 
#         WHERE booking_id = %s AND user_id = %s
#     """, (booking_id, user_id))
    
#     booking = cursor.fetchone()

#     if not booking:
#         return jsonify({"error": "Booking not found or not authorized"}), 404

#     if booking["status"] in ("completed", "checked-in", "cancelled"):
#         return jsonify({"error": f"Booking cannot be cancelled (current status: {booking['status']})"}), 400

#     departure_time = (datetime.min + booking["departure_time"]).time()  # Convert timedelta to time
#     departure_datetime = datetime.combine(datetime.now().date(), departure_time)
#     cancel_date = datetime.now()
#     days_before_departure = (departure_datetime - cancel_date).days


#     cancellation_fee = 0
#     if 30 <= days_before_departure < 60:
#         cancellation_fee = 0.40 * booking["total_price"]
#     elif days_before_departure < 30:
#         cancellation_fee = booking["total_price"]

#     cursor.execute("""
#         UPDATE bookings 
#         SET status = 'cancelled', cancellation_fee = %s
#         WHERE booking_id = %s
#     """, (cancellation_fee, booking_id))

#     conn.commit()
#     cursor.close()
#     conn.close()

#     return jsonify({
#         "message": "Booking cancelled",
#         "cancellation_fee": cancellation_fee
#     }), 200





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



from flask import Blueprint, request, jsonify, Response, url_for
import mysql.connector
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import Config
import uuid

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
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



from datetime import timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import mysql.connector
from flask_bcrypt import Bcrypt
from app import mail
import random
import string
from config import Config
from flask import Response
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io


bp = Blueprint('user', __name__)
bcrypt = Bcrypt()

def get_db_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )


@bp.route('/', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT first_name, last_name, email, address, city, mobile_number, date_of_birth, gender FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"user": user}), 200


@bp.route('/edit-user', methods=['PUT'])
@jwt_required()
def update_user():
    user_id = get_jwt_identity()
    data = request.json

    fields_to_update = []
    values = []
    
    allowed_fields = ["first_name", "last_name", "address", "city", "mobile_number", "date_of_birth", "gender"]
    
    for field in allowed_fields:
        if field in data:
            fields_to_update.append(f"{field} = %s")
            values.append(data[field])
    
    if not fields_to_update:
        return jsonify({"error": "No valid fields to update"}), 400

    values.append(user_id)

    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"UPDATE users SET {', '.join(fields_to_update)} WHERE id = %s"
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "User profile updated successfully"}), 200



@bp.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_user():
    user_id = get_jwt_identity()

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "User account deleted successfully"}), 200

# @bp.route('/bookings', methods=['GET'])
# @jwt_required()
# def get_user_bookings():
#     user_id = get_jwt_identity()

#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     query = """
#     SELECT b.booking_id, b.flight_id, f.departure, f.destination, f.departure_time, 
#            f.arrival_time, b.seats, b.flight_class, b.round_trip, b.status, b.booking_time, b.payment_reference
#     FROM bookings b
#     LEFT JOIN flights f ON b.flight_id = f.id
#     WHERE b.user_id = %s
#     ORDER BY b.booking_time DESC
#     """
    
#     cursor.execute(query, (user_id,))
#     bookings = cursor.fetchall()
#     for booking in bookings:
#         if isinstance(booking["departure_time"], timedelta):
#             booking["departure_time"] = str(booking["departure_time"])
#         if isinstance(booking["arrival_time"], timedelta):
#             booking["arrival_time"] = str(booking["arrival_time"])

#     cursor.close()
#     conn.close()

#     return jsonify({"bookings": bookings}), 200


# @bp.route('/bookings/cancel', methods=['PUT'])
# @jwt_required()
# def cancel_booking():
#     user_id = get_jwt_identity()
#     data = request.json
#     booking_id = data.get("booking_id")

#     if not booking_id:
#         return jsonify({"error": "Booking ID is required"}), 400

#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     cursor.execute("SELECT status FROM bookings WHERE booking_id = %s AND user_id = %s", 
#                    (booking_id, user_id))
#     booking = cursor.fetchone()

#     if not booking:
#         return jsonify({"error": "Booking not found or not authorized"}), 404

#     if booking["status"] in ("completed", "checked-in", "cancelled"):
#         return jsonify({"error": f"Booking cannot be cancelled (current status: {booking['status']})"}), 400

#     cursor.execute("UPDATE bookings SET status = 'cancelled' WHERE booking_id = %s", (booking_id,))
#     conn.commit()
#     cursor.close()
#     conn.close()

#     return jsonify({"message": "Booking cancelled successfully"}), 200


# @bp.route('/bookings/pay', methods=['POST'])
# @jwt_required()
# def process_payment():
#     user_id = get_jwt_identity()
#     data = request.json
#     booking_id = data.get("booking_id")

#     if not booking_id:
#         return jsonify({"error": "Booking ID is required"}), 400

#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     cursor.execute("SELECT status, payment_status FROM bookings WHERE booking_id = %s AND user_id = %s", 
#                    (booking_id, user_id))
#     booking = cursor.fetchone()

#     if not booking:
#         return jsonify({"error": "Booking not found or not authorized"}), 404

#     if booking["status"] != "pending":
#         return jsonify({"error": f"Booking cannot be paid for (current status: {booking['status']})"}), 400

#     if booking["payment_status"] == "paid":
#         return jsonify({"error": "Booking is already paid for"}), 400

#     payment_successful = random.choice([True, False])  # Simulate success/failure

#     if payment_successful:
#         payment_reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))  # Generate ref
#         cursor.execute("UPDATE bookings SET payment_status = 'paid', status = 'confirmed', payment_reference = %s WHERE booking_id = %s", 
#                        (payment_reference, booking_id))
#         conn.commit()

#         return jsonify({"message": "Payment successful!", "payment_reference": payment_reference}), 200
#     else:
#         cursor.execute("UPDATE bookings SET payment_status = 'failed' WHERE booking_id = %s", (booking_id,))
#         conn.commit()
#         return jsonify({"error": "Payment failed. Try again."}), 400



# @bp.route('bookings/receipt/<booking_id>', methods=['GET'])
# @jwt_required()
# def generate_receipt(booking_id):
#     user_id = get_jwt_identity()

#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     cursor.execute("""
#         SELECT b.booking_id, b.payment_status, b.payment_reference, f.departure, f.destination,
#                f.departure_time, f.arrival_time, b.seats, b.flight_class, b.round_trip, b.status, b.booking_time
#         FROM bookings b
#         LEFT JOIN flights f ON b.flight_id = f.id
#         WHERE b.booking_id = %s AND b.user_id = %s
#     """, (booking_id, user_id))
    
#     booking = cursor.fetchone()
#     cursor.close()
#     conn.close()

#     if not booking:
#         return jsonify({"error": "Booking not found or not authorized"}), 404

#     if booking["payment_status"] != "paid":
#         return jsonify({"error": "Receipt unavailable. Payment not completed."}), 400

#     return jsonify({
#         "receipt": {
#             "booking_id": booking["booking_id"],
#             "payment_reference": booking["payment_reference"],
#             "flight": {
#                 "departure": booking["departure"],
#                 "destination": booking["destination"],
#                 "departure_time": str(booking["departure_time"]),
#                 "arrival_time": str(booking["arrival_time"])
#             },
#             "seats": booking["seats"],
#             "class": booking["flight_class"],
#             "round_trip": booking["round_trip"],
#             "status": booking["status"],
#             "booking_time": str(booking["booking_time"])
#         }
#     }), 200


# @bp.route('/delete', methods=['DELETE'])
# @jwt_required()
# def delete_user():
#     user_id = get_jwt_identity()

#     conn = get_db_connection()
#     cursor = conn.cursor()
    
#     cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
#     conn.commit()

#     cursor.close()
#     conn.close()

#     return jsonify({"message": "User account deleted successfully"}), 200


# @bp.route('/bookings/receipt/pdf/<booking_id>', methods=['GET'])
# @jwt_required()
# def generate_pdf_receipt(booking_id):
#     user_id = get_jwt_identity()

#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     cursor.execute("""
#         SELECT b.booking_id, b.payment_status, b.payment_reference, f.departure, f.destination,
#                f.departure_time, f.arrival_time, b.seats, b.flight_class, b.round_trip, b.status, b.booking_time
#         FROM bookings b
#         LEFT JOIN flights f ON b.flight_id = f.id
#         WHERE b.booking_id = %s AND b.user_id = %s
#     """, (booking_id, user_id))
    
#     booking = cursor.fetchone()
#     cursor.close()
#     conn.close()

#     if not booking:
#         return jsonify({"error": "Booking not found or not authorized"}), 404

#     if booking["payment_status"] != "paid":
#         return jsonify({"error": "Receipt unavailable. Payment not completed."}), 400

#     buffer = io.BytesIO()
#     pdf = canvas.Canvas(buffer, pagesize=letter)
#     pdf.setTitle(f"Booking Receipt - {booking_id}")

#     pdf.setFont("Helvetica-Bold", 16)
#     pdf.drawString(200, 750, "Horizon Travels - Booking Receipt")
    
#     pdf.setFont("Helvetica", 12)
#     pdf.drawString(100, 720, f"Booking ID: {booking['booking_id']}")
#     pdf.drawString(100, 700, f"Payment Reference: {booking['payment_reference']}")
#     pdf.drawString(100, 680, f"Status: {booking['status'].capitalize()}")

#     pdf.drawString(100, 650, f"Flight: {booking['departure']} → {booking['destination']}")
#     pdf.drawString(100, 630, f"Departure Time: {str(booking['departure_time'])}")
#     pdf.drawString(100, 610, f"Arrival Time: {str(booking['arrival_time'])}")

#     pdf.drawString(100, 580, f"Seats: {booking['seats']}")
#     pdf.drawString(100, 560, f"Class: {booking['flight_class'].capitalize()}")
#     pdf.drawString(100, 540, f"Round Trip: {'Yes' if booking['round_trip'] else 'No'}")
#     pdf.drawString(100, 520, f"Booking Time: {str(booking['booking_time'])}")

#     pdf.showPage()
#     pdf.save()

#     buffer.seek(0)
    
#     return Response(buffer, mimetype="application/pdf",
#                     headers={"Content-Disposition": f'attachment; filename=Horizon_Travels-receipt_{booking_id}.pdf'})



from datetime import datetime
import uuid
from flask import Blueprint, redirect, request, jsonify, render_template, session, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required
import mysql.connector
from config import Config

bp = Blueprint('flight_book', __name__)

def get_db_connection():
    conn =  mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )
    cursor = conn.cursor()
    cursor.execute("SELECT DATABASE();")
    db_name = cursor.fetchone()[0]
    print(f"Connected to database: {db_name}")
    cursor.close()
    
    return conn


@bp.route('/', methods=["POST", "GET"])
@jwt_required()
def flight_book():
    user_id = get_jwt_identity()
    data = request.form  # Get data from form submission

    departure = data.get("departure")
    destination = data.get("destination")
    departure_date = data.get("departure_date")
    arrival_date = data.get("arrival_date")
    seats = int(data.get("seats", 1))
    flight_class = data.get("flight_class").lower()
    round_trip = data.get("trip") == "roundtrip"

    if not departure or not destination or not departure_date:
        return render_template("index.html", error="Please fill in all required fields.")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch flight details
    cursor.execute("""
        SELECT id, departure, destination, departure_time, arrival_time 
        FROM flights WHERE departure = %s AND destination = %s
    """, (departure, destination))
    flight = cursor.fetchone()

    if not flight:
        return render_template("index.html", error="No available flights for this route.")

    # Fetch flight price
    cursor.execute("""
        SELECT price FROM flight_prices WHERE departure = %s AND destination = %s
    """, (departure, destination))
    price_data = cursor.fetchone()

    cursor.close()
    conn.close()

    if not price_data:
        return render_template("home/index.html", error="Price not found for the selected route.")

    base_price = price_data["price"] * seats

    # Calculate discount
    booking_date = datetime.now().date()
    departure_datetime = datetime.strptime(departure_date, "%Y-%m-%d")
    days_in_advance = (departure_datetime - datetime.combine(booking_date, datetime.min.time())).days
    
    discount_percentage = 0
    if 80 <= days_in_advance <= 90:
        discount_percentage = 25
    elif 60 <= days_in_advance <= 79:
        discount_percentage = 15
    elif 45 <= days_in_advance <= 59:
        discount_percentage = 10

    discount_amount = (discount_percentage / 100) * base_price
    final_price = base_price - discount_amount

    # Prepare booking details to pass to flight_book.html
    booking_details = {
        "flight_id": flight["id"],
        "departure": flight["departure"],
        "destination": flight["destination"],
        "departure_time": flight["departure_time"],
        "arrival_time": flight["arrival_time"],
        "seats": seats,
        "flight_class": flight_class,
        "round_trip": round_trip,
        "total_price": final_price,
        "discount_applied": discount_amount,
    }

    return render_template("flight-book.html", booking=booking_details)





# @bp.route('/', methods=['GET'])
# @jwt_required()
# def flight_book():
#     user_id = get_jwt_identity()

#     # Get query parameters from URL
#     flight_id = request.args.get("flight_id")
#     seats = request.args.get("seats")
#     flight_class = request.args.get("flight_class")
#     round_trip = request.args.get("round_trip")

#     if not flight_id:
#         return redirect(url_for("main.index", error="Missing flight selection."))

#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     # Fetch flight details
#     cursor.execute("SELECT * FROM flights WHERE id = %s", (flight_id,))
#     flight = cursor.fetchone()

#     if not flight:
#         cursor.close()
#         conn.close()
#         return "No flights available for this ID", 404

#     # Fetch price details
#     cursor.execute("SELECT price FROM flight_prices WHERE departure = %s AND destination = %s", 
#                    (flight["departure"], flight["destination"]))
#     price_data = cursor.fetchone()

#     cursor.close()
#     conn.close()

#     if not price_data:
#         return "Flight price not found", 404

#     return render_template("flight_book.html",
#         user_id=user_id,
#         flight=flight,
#         price=price_data["price"],
#         seats=seats,
#         flight_class=flight_class,
#         round_trip=round_trip
#     )






# @bp.route('/', methods=["GET"])
# @jwt_required()
# def flight_book():
#     user_id = get_jwt_identity()

#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     # If a pending booking is stored in the session, use it
#     if "pending_booking" in session:
#         latest_booking = session["pending_booking"]
#     else:
#         # Fetch the latest pending booking
#         cursor.execute("""
#             SELECT b.*, f.departure, f.destination, f.departure_time, f.arrival_time 
#             FROM bookings b
#             JOIN flights f ON b.flight_id = f.id
#             WHERE b.user_id = %s AND b.status = 'pending'  
#             ORDER BY b.booking_time DESC 
#             LIMIT 1
#         """, (user_id,))

#         latest_booking = cursor.fetchone()
#         print("Latest Booking:", latest_booking)
        
#         if latest_booking:
#             session["pending_booking"] = latest_booking

#     cursor.close()
#     conn.close()

#     return render_template("flight-book.html", booking=latest_booking)





# @bp.route('/', methods=["GET"])
# def flight_book():
#     return render_template("flight-book.html")


# def flight_book():
#     departure = request.args.get("departure")
#     destination = request.args.get("destination")
#     response_format = request.args.get("format", "html")

#     if not departure or not destination:
#         return redirect(url_for("main.home", error="Sorry, we have no flights available. Please edit your search to find other routes."))

#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True, buffered=True)

#     print(f"Querying database for route: '{departure}' -> '{destination}'")

#     query_flight = "SELECT departure_time, arrival_time FROM flights WHERE departure = %s AND destination = %s"
#     cursor.execute(query_flight, (departure.strip(), destination.strip()))
#     flight_result = cursor.fetchone()
    

#     query_price = "SELECT price FROM flight_prices WHERE departure = %s AND destination = %s"
#     cursor.execute(query_price, (departure.strip(), destination.strip()))
#     price_result = cursor.fetchone()

#     default_price_query = "SELECT price FROM flight_prices WHERE departure = 'DEFAULT' AND destination = 'DEFAULT'"
#     cursor.execute(default_price_query)
#     default_price_result = cursor.fetchone()

#     cursor.close()
#     conn.close()



#     if flight_result:
#         flight_data = {
#             "departure_time": str(flight_result["departure_time"]),
#             "arrival_time": str(flight_result["arrival_time"]),
#             "price": price_result["price"] if price_result else default_price_result["price"]
#         }
#         if response_format == "json":
#             return jsonify(flight_data)
        
#         return render_template("flight-book.html", **flight_data)

#     print("No flight found, redirecting to index.")
#     if response_format == "json":
#         return jsonify({"error": "No flight found for this route"}), 404

#     return redirect(url_for("main.home"))
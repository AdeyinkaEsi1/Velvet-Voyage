from datetime import datetime
import uuid
from flask import Blueprint, request, render_template, session, url_for
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
    data = request.form

    departure = data.get("departure")
    destination = data.get("destination")
    departure_date = data.get("departure_date")
    return_date = data.get("return_date")
    seats = int(data.get("seats", 1))
    flight_class = data.get("flight_class", "economy").strip().lower()
    round_trip = data.get("round_trip") == "true"
    
    error = "Please fill in all required fields."

    if not departure or not destination or not departure_date:
        return render_template("home/index.html", error=error)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch flight details
    cursor.execute("""
        SELECT id, departure, destination, departure_time, arrival_time 
        FROM flights WHERE departure = %s AND destination = %s
    """, (departure, destination))
    flight = cursor.fetchone()

    if not flight:
        return render_template("index.html", error="Sorry, No Available Flights for the Selected Route.")

    # Fetch flight price
    cursor.execute("""
        SELECT price FROM flight_prices WHERE departure = %s AND destination = %s
    """, (departure, destination))
    base_price = cursor.fetchone()

    cursor.close()
    conn.close()
    
    if flight_class == "business":
        base_flight_price = base_price["price"] * 2
    else:
        base_flight_price = base_price["price"]
        
    if not base_price:
        return render_template("home/index.html", error="Price not found for the selected route.")

    total_flight_price = base_flight_price * seats

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

    discount_amount = (discount_percentage / 100) * total_flight_price
    final_price = total_flight_price - discount_amount

    # Prepare booking details to pass to flight_book.html
    booking_details = {
        "user_id": user_id,
        "flight_id": flight["id"],
        "departure": flight["departure"],
        "destination": flight["destination"],
        "departure_date": departure_date,
        "departure_time": flight["departure_time"],
        "return_date": return_date,
        "arrival_time": flight["arrival_time"],
        "seats": seats,
        "flight_class": flight_class,
        "round_trip": round_trip,
        "base_price": base_flight_price,
        "total_price": total_flight_price,
        "discount_applied": discount_amount,
        "final_price": final_price,
    }

    return render_template("flight-book.html", booking=booking_details)



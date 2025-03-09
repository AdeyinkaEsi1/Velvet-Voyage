from flask import Blueprint, redirect, request, jsonify, render_template, url_for
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
    

@bp.route('/', methods=["GET"])
def flight_book():
    departure = request.args.get("departure")
    destination = request.args.get("destination")
    response_format = request.args.get("format", "html")

    if not departure or not destination:
        return redirect(url_for("main.home", error="Sorry, we have no flights available. Please edit your search to find other routes."))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    print(f"Querying database for route: '{departure}' -> '{destination}'")

    query_flight = "SELECT departure_time, arrival_time FROM flights WHERE departure = %s AND destination = %s"
    cursor.execute(query_flight, (departure.strip(), destination.strip()))
    flight_result = cursor.fetchone()
    

    query_price = "SELECT price FROM flight_prices WHERE departure = %s AND destination = %s"
    cursor.execute(query_price, (departure.strip(), destination.strip()))
    price_result = cursor.fetchone()

    default_price_query = "SELECT price FROM flight_prices WHERE departure = 'DEFAULT' AND destination = 'DEFAULT'"
    cursor.execute(default_price_query)
    default_price_result = cursor.fetchone()

    cursor.close()
    conn.close()



    if flight_result:
        flight_data = {
            "departure_time": str(flight_result["departure_time"]),
            "arrival_time": str(flight_result["arrival_time"]),
            "price": price_result["price"] if price_result else default_price_result["price"]
        }
        if response_format == "json":
            return jsonify(flight_data)
        
        return render_template("flight-book.html", **flight_data)

    print("No flight found, redirecting to index.")
    if response_format == "json":
        return jsonify({"error": "No flight found for this route"}), 404

    return redirect(url_for("main.home"))
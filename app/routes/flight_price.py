from flask import Blueprint, request, jsonify, render_template
import mysql.connector
from config import Config

bp = Blueprint('flight_price', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )
    

@bp.route('/', methods=["GET"])
def flight_price():
    departure = request.args.get("departure")
    destination = request.args.get("destination")
    
    if not departure or not destination:
        return jsonify({"error": "Missing departure or destination"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get price from flight_prices table
    query_price = "SELECT price FROM flight_prices WHERE departure = %s AND destination = %s"
    cursor.execute(query_price, (departure, destination))
    price_result = cursor.fetchone()
    
    # Get flight time from flights table
    query_flight = "SELECT departure_time, arrival_time FROM flights WHERE departure = %s AND destination = %s"
    cursor.execute(query_flight, (departure, destination))
    flight_result = cursor.fetchone()

    cursor.close()
    conn.close()

    if price_result and flight_result:
        return jsonify({
            "price": price_result["price"],
            "departure_time": str(flight_result["departure_time"]),
            "arrival_time": str(flight_result["arrival_time"])
        })
    else:
        return jsonify({"error": "No flight or price found for this route"}), 404
# return render_template("flight_price.html")
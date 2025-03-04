from flask import Blueprint, request, jsonify, render_template
import mysql.connector
from config import Config

bp = Blueprint('flight_price', __name__)

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
    print(f"Connected to database: {db_name}")  # Debugging output
    cursor.close()
    
    return conn
    
    # return mysql.connector.connect(
    #     host=Config.DB_HOST,
    #     user=Config.DB_USER,
    #     password=Config.DB_PASSWORD,
    #     database=Config.DB_NAME
    # )
    
    

@bp.route('/', methods=["GET"])
def flight_price():
    departure = request.args.get("departure")
    destination = request.args.get("destination")
    
    if not departure or not destination:
        return jsonify({"error": "Missing departure or destination"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Debugging: Print the values being sent to MySQL
    print(f"Querying database for route: '{departure}' -> '{destination}'")
    
    # Get price from flight_prices table
    query_price = " SELECT price FROM flight_prices WHERE departure = %s  AND destination = %s"
    # query_price = "SELECT price FROM flight_prices WHERE departure = 'Dundee' AND destination = 'Portsmouth'"
    cursor.execute(query_price, (departure.strip().lower(), destination.strip().lower()))
    price_result = cursor.fetchone()
    
    # Get flight time from flights table
    query_flight = "SELECT departure_time, arrival_time FROM flights WHERE departure = %s AND destination = %s"
    cursor.execute(query_flight, (departure.strip().lower(), destination.strip().lower()))
    flight_result = cursor.fetchone()

    cursor.close()
    conn.close()

    if price_result:
        return jsonify({
            "price": price_result["price"],
            # "departure_time": str(flight_result["departure_time"]),
            # "arrival_time": str(flight_result["arrival_time"])
        })
    else:
        print("No matching route found in database.")
        return jsonify({"error": "No flight or price found for this route"}), 404
# return render_template("flight_price.html")
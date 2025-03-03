from flask import Blueprint, request, jsonify, render_template
import mysql.connector
from config import Config

bp = Blueprint('flights_bp', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )

# @bp.route('/')
# def flight_list():
    # conn = get_db_connection()
    # cursor = conn.cursor()
    # cursor.execute("SELECT id, user_name, destination, date FROM flights")
    # bookings = cursor.fetchall()
    # cursor.close()
    # conn.close()
    # return render_template("bookings.html", bookings=bookings)
    # return render_template('flights.html', title="Flights", username="Hamid")
    # return jsonify({'flights': 'list of flights'})


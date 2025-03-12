from datetime import timedelta
import re
from flask_bcrypt import Bcrypt
from flask import Blueprint, render_template, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import mysql.connector
from config import Config

bp = Blueprint('admin', __name__)
bcrypt = Bcrypt()


def get_db_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )

def is_admin(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT role FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user and user["role"] == "admin"


@bp.route('/admin/dashboard', methods=['GET'])
@jwt_required()
def admin_dashboard():
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT COUNT(id) AS total_users, 
           (SELECT COUNT(id) FROM bookings) AS total_bookings, 
           (SELECT COUNT(id) FROM flights) AS total_flights
    FROM users
    """

    cursor.execute(query)
    dashboard_data = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return render_template("admin/dashboard.html", dashboard_data=dashboard_data)

    # return jsonify({"dashboard_data": dashboard_data}), 200


@bp.route('/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, first_name, last_name, email, role FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin/users.html', users=users)
    # return jsonify({"users": users}), 200

@bp.route('/admin/users/delete/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "User deleted successfully"}), 200


@bp.route('/admin/register_admin', methods=['POST'])
@jwt_required()
def register_admin():
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    data = request.json
    first_name = data["first_name"].strip().title()
    last_name = data["last_name"].strip().title()
    email = data["email"].strip().lower()
    confirm_email = data["confirm_email"].strip().lower()
    address = data["address"].strip()
    city = data["city"].strip().title()
    mobile_number = data["mobile_number"].strip()
    date_of_birth = data["date_of_birth"]
    gender = data["gender"]
    password = data["password"]
    confirm_password = data["confirm_password"]
    
     # Validate email
    if email != confirm_email:
        return jsonify({"error": "Emails do not match"}), 400
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"error": "Invalid email format"}), 400
    
        # Validate password
    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""INSERT INTO users (first_name, last_name, email, address, city, mobile_number, 
                            date_of_birth, gender, password_hash, role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'admin')
                            """, (first_name, last_name, email, address, city, mobile_number,
                                  date_of_birth, gender, hashed_password))
        conn.commit()
        return jsonify({"message": "Admin account created successfully"}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409
    finally:
        cursor.close()
        conn.close()


@bp.route('/admin/register_user', methods=['POST'])
@jwt_required()
def register_user():
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    first_name = data["first_name"].strip().title()
    last_name = data["last_name"].strip().title()
    email = data["email"].strip().lower()
    confirm_email = data["confirm_email"].strip().lower()
    address = data["address"].strip()
    city = data["city"].strip().title()
    mobile_number = data["mobile_number"].strip()
    date_of_birth = data["date_of_birth"]
    gender = data["gender"]
    password = data["password"]
    confirm_password = data["confirm_password"]
    
     # Validate email
    if email != confirm_email:
        return jsonify({"error": "Emails do not match"}), 400
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"error": "Invalid email format"}), 400
    
        # Validate password
    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""INSERT INTO users (first_name, last_name, email, address, city, mobile_number, 
                            date_of_birth, gender, password_hash, role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'user')
                            """, (first_name, last_name, email, address, city, mobile_number,
                                  date_of_birth, gender, hashed_password))
        conn.commit()
        return jsonify({"message": "User account created successfully"}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409
    finally:
        cursor.close()
        conn.close()



@bp.route('/admin/bookings', methods=['GET'])
@jwt_required()
def get_all_bookings():
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT b.booking_id, u.first_name, u.last_name, u.email, 
           f.departure, f.destination, f.departure_time, f.arrival_time, 
           b.seats, b.flight_class, b.round_trip, b.status, b.booking_time, b.payment_status
    FROM bookings b
    LEFT JOIN users u ON b.user_id = u.id
    LEFT JOIN flights f ON b.flight_id = f.id
    ORDER BY b.booking_time DESC
    """

    cursor.execute(query)
    bookings = cursor.fetchall()
    
    for booking in bookings:
        if isinstance(booking["departure_time"], timedelta):
            booking["departure_time"] = str(booking["departure_time"])
        if isinstance(booking["arrival_time"], timedelta):
            booking["arrival_time"] = str(booking["arrival_time"])
    cursor.close()
    conn.close()

    return render_template('admin/bookings.html', bookings=bookings)
    # return jsonify({"bookings": bookings}), 200


@bp.route('/admin/bookings/edit/<booking_id>', methods=['PUT'])
@jwt_required()
def update_booking_status(booking_id):
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    new_status = data.get("status")

    allowed_statuses = ["pending", "confirmed", "checked-in", "cancelled", "completed", "no-show"]

    if new_status not in allowed_statuses:
        return jsonify({"error": f"Invalid status. Allowed: {', '.join(allowed_statuses)}"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE bookings SET status = %s WHERE booking_id = %s", (new_status, booking_id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": f"Booking {booking_id} updated to {new_status}"}), 200



@bp.route('/admin/bookings/delete/<booking_id>', methods=['DELETE'])
@jwt_required()
def delete_booking(booking_id):
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM bookings WHERE booking_id = %s", (booking_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": f"Booking {booking_id} deleted successfully"}), 200



@bp.route('/admin/flights', methods=['GET'])
@jwt_required()
def get_all_flights():
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM flights")
    flights = cursor.fetchall()

    for flight in flights:
        if isinstance(flight["departure_time"], timedelta):
            flight["departure_time"] = str(flight["departure_time"])
        if isinstance(flight["arrival_time"], timedelta):
            flight["arrival_time"] = str(flight["arrival_time"])

    cursor.close()
    conn.close()
    
    return render_template('admin/flights.html', flights=flights)

    # return jsonify({"flights": flights}), 200



@bp.route('/admin/new/flights', methods=['POST'])
@jwt_required()
def add_flight():
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    required_fields = ["departure", "destination", "departure_time", "arrival_time"]
    
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required flight details"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO flights (departure, destination, departure_time, arrival_time) VALUES (%s, %s, %s, %s)",
        (data["departure"], data["destination"], data["departure_time"], data["arrival_time"])
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Flight added successfully"}), 201


@bp.route('/admin/flights/edit/<int:flight_id>', methods=['PUT'])
@jwt_required()
def update_flight(flight_id):
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    update_fields = []
    values = []

    allowed_fields = ["departure", "destination", "departure_time", "arrival_time"]

    for field in allowed_fields:
        if field in data:
            update_fields.append(f"{field} = %s")
            values.append(data[field])

    if not update_fields:
        return jsonify({"error": "No valid fields to update"}), 400

    values.append(flight_id)

    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = f"UPDATE flights SET {', '.join(update_fields)} WHERE id = %s"
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Flight updated successfully"}), 200



@bp.route('/admin/flights/delete/<int:flight_id>', methods=['DELETE'])
@jwt_required()
def delete_flight(flight_id):
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM flights WHERE id = %s", (flight_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Flight deleted successfully"}), 200


@bp.route('/admin/flights/prices', methods=['GET'])
@jwt_required()
def get_all_flight_prices():
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT fp.id, 
           COALESCE(f.departure, fp.departure) AS departure, 
           COALESCE(f.destination, fp.destination) AS destination, 
           fp.price 
    FROM flight_prices fp
    LEFT JOIN flights f ON fp.departure = f.departure AND fp.destination = f.destination
    """
    
    cursor.execute(query)
    prices = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify({"flight_prices": prices}), 200



@bp.route('/admin/flights/edit/prices/<int:price_id>', methods=['PUT'])
@jwt_required()
def update_flight_price(price_id):
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    new_price = data.get("price")

    if new_price is None or new_price < 0:
        return jsonify({"error": "Invalid price value"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE flight_prices SET price = %s WHERE id = %s", (new_price, price_id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": f"Flight price updated to {new_price}"}), 200


@bp.route('/admin/reports/monthly-sales', methods=['GET'])
@jwt_required()
def monthly_sales():
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT DATE_FORMAT(booking_time, '%Y-%m') AS month, 
           SUM(fp.price * b.seats) AS total_sales
    FROM bookings b
    JOIN flight_prices fp ON b.flight_id = fp.id
    WHERE b.payment_status = 'paid'
    GROUP BY month
    ORDER BY month DESC
    """

    cursor.execute(query)
    sales_data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/sales.html', sales_data=sales_data)
    # return jsonify({"monthly_sales": sales_data}), 200


@bp.route('/admin/reports/sales-per-journey', methods=['GET'])
@jwt_required()
def sales_per_journey():
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT fp.departure, fp.destination, 
           SUM(fp.price * b.seats) AS total_sales, 
           COUNT(b.booking_id) AS total_bookings
    FROM bookings b
    JOIN flight_prices fp ON b.flight_id = fp.id
    WHERE b.payment_status = 'paid'
    GROUP BY fp.departure, fp.destination
    ORDER BY total_sales DESC
    """

    cursor.execute(query)
    sales_data = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify({"sales_per_journey": sales_data}), 200


@bp.route('/admin/reports/top-customers', methods=['GET'])
@jwt_required()
def top_customers():
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT u.id, u.first_name, u.last_name, u.email, 
           SUM(fp.price * b.seats) AS total_spent, 
           COUNT(b.booking_id) AS total_bookings
    FROM bookings b
    JOIN users u ON b.user_id = u.id
    JOIN flight_prices fp ON b.flight_id = fp.id
    WHERE b.payment_status = 'paid'
    GROUP BY u.id, u.first_name, u.last_name, u.email
    ORDER BY total_spent DESC
    LIMIT 10
    """

    cursor.execute(query)
    customers = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify({"top_customers": customers}), 200


@bp.route('/admin/reports/profitable-routes', methods=['GET'])
@jwt_required()
def profitable_routes():
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT fp.departure, fp.destination, 
           SUM(fp.price * b.seats) AS revenue,
           COUNT(b.booking_id) AS total_bookings
    FROM bookings b
    JOIN flight_prices fp ON b.flight_id = fp.id
    WHERE b.payment_status = 'paid'
    GROUP BY fp.departure, fp.destination
    HAVING revenue > 5000
    ORDER BY revenue DESC
    """

    cursor.execute(query)
    routes = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify({"profitable_routes": routes}), 200


@bp.route('/admin/reports/loss-routes', methods=['GET'])
@jwt_required()
def loss_routes():
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT fp.departure, fp.destination, 
           SUM(fp.price * b.seats) AS revenue,
           COUNT(b.booking_id) AS total_bookings
    FROM bookings b
    JOIN flight_prices fp ON b.flight_id = fp.id
    WHERE b.payment_status = 'paid'
    GROUP BY fp.departure, fp.destination
    HAVING revenue < 1000  -- Assuming a threshold for losses
    ORDER BY revenue ASC
    """

    cursor.execute(query)
    routes = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify({"loss_routes": routes}), 200



"""
{
    "first_name": "Admin", 
    "last_name": "01",
    "email": "admin@example.com",
    "confirm_email": "admin@example.com",
    "address": "123 Street",
    "city": "Instabul",
    "mobile_number": "08059472483", 
    "date_of_birth": "1990-01-07",
    "gender": "Male",
    "password": "Password123", 
    "confirm_password": "Password123",
    "role": "admin"
}
"""
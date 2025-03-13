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


# @bp.route('/admin/dashboard', methods=['GET'])
# @jwt_required()
# def admin_dashboard():
#     admin_id = get_jwt_identity()
#     if not is_admin(admin_id):
#         return jsonify({"error": "Unauthorized"}), 403

#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     query = """
#     SELECT COUNT(id) AS total_users, 
#            (SELECT COUNT(id) FROM bookings) AS total_bookings, 
#            (SELECT COUNT(id) FROM flights) AS total_flights
#     FROM users
#     """

#     cursor.execute(query)
#     dashboard_data = cursor.fetchone()
#     cursor.close()
#     conn.close()
    
#     return render_template("admin/dashboard.html", dashboard_data=dashboard_data)



@bp.route('/admin/dashboard', methods=['GET'])
@jwt_required()
def admin_dashboard():
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # total users, total bookings, total flights, total revenue
    cursor.execute("""
        SELECT 
            (SELECT COUNT(id) FROM users) AS total_users,
            (SELECT COUNT(id) FROM bookings) AS total_bookings,
            (SELECT COUNT(id) FROM flights) AS total_flights,
            (SELECT COALESCE(SUM(fp.price * b.seats), 0) FROM bookings b 
             JOIN flight_prices fp ON b.flight_id = fp.id 
             WHERE b.payment_status = 'paid') AS total_revenue,
            (SELECT COUNT(id) FROM bookings WHERE status = 'pending') AS pending_bookings,
            (SELECT COUNT(id) FROM bookings WHERE status = 'confirmed') AS confirmed_bookings
    """)
    dashboard_data = cursor.fetchone()

    # recent bookings
    cursor.execute("""
        SELECT b.booking_id, u.first_name, u.last_name, 
               f.departure, f.destination, b.status
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN flights f ON b.flight_id = f.id
        ORDER BY b.booking_time DESC
        LIMIT 5
    """)
    recent_bookings = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin/dashboard.html",
        dashboard_data=dashboard_data,
        recent_bookings=recent_bookings
    )



@bp.route('/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, first_name, last_name, city, gender, mobile_number, email, role FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin/users.html', users=users)
    # return jsonify({"users": users}), 200



@bp.route('/admin/update_user_role/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user_role(user_id):
    admin_id = get_jwt_identity()

    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized access"}), 403

    data = request.json
    new_role = data.get("role")

    if new_role not in ["user", "admin"]:
        return jsonify({"error": "Invalid role. Choose 'user' or 'admin'."}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        conn.close()
        return jsonify({"error": "User not found"}), 404

    cursor.execute("UPDATE users SET role = %s WHERE id = %s", (new_role, user_id))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": f"User role updated successfully to '{new_role}'"}), 200



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
           f.departure, f.destination, f.departure_time, f.id, f.arrival_time, 
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


@bp.route('/admin/update/booking/<booking_id>', methods=['PUT'])
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



@bp.route('/admin/delete/booking/<booking_id>', methods=['DELETE'])
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




def format_timedelta(td):
    """Convert a timedelta object to a string in HH:MM:SS format."""
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


@bp.route('/admin/flights', methods=['GET'])
@jwt_required()
def get_all_flights(): 
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT f.id, f.departure, f.destination, f.departure_time, f.arrival_time, fp.price
        FROM flights f
        LEFT JOIN flight_prices fp 
        ON f.departure = fp.departure AND f.destination = fp.destination
    """)
    
    flights = cursor.fetchall()
    
    for flight in flights:
        if isinstance(flight["departure_time"], timedelta):
            flight["departure_time"] = format_timedelta(flight["departure_time"])
        if isinstance(flight["arrival_time"], timedelta):
            flight["arrival_time"] = format_timedelta(flight["arrival_time"])


    cursor.close()
    conn.close()
    
    return render_template('admin/flights.html', flights=flights)



@bp.route('/admin/new/flights', methods=['POST'])
@jwt_required()
def add_flight():
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    required_fields = ["departure", "destination", "departure_time", "arrival_time", "price"]
    
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required flight details"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO flights (departure, destination, departure_time, arrival_time) VALUES (%s, %s, %s, %s)",
            (data["departure"], data["destination"], data["departure_time"], data["arrival_time"])
        )
        
        flight_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO flight_prices (departure, destination, price) VALUES (%s, %s, %s) "
            "ON DUPLICATE KEY UPDATE price = VALUES(price)",
            (data["departure"], data["destination"], data["price"])
        )

        conn.commit()
        return jsonify({"message": "Flight added successfully", "flight_id": flight_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()



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


@bp.route('/admin/update/flight/<int:flight_id>', methods=['PUT'])
@jwt_required()
def update_flight(flight_id):
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    departure = data.get("departure")
    destination = data.get("destination")
    departure_time = data.get("departure_time")
    arrival_time = data.get("arrival_time")
    price = data.get("price")

    if not (departure and destination and departure_time and arrival_time and price):
        return jsonify({"error": "All fields are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE flights 
            SET departure=%s, destination=%s, departure_time=%s, arrival_time=%s
            WHERE id=%s
        """, (departure, destination, departure_time, arrival_time, flight_id))

        cursor.execute("""
            UPDATE flight_prices
            SET price=%s
            WHERE departure=%s AND destination=%s
        """, (price, departure, destination))

        conn.commit()
        return jsonify({"message": "Flight updated successfully!"}), 200

    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": f"Database error: {err}"}), 500

    finally:
        cursor.close()
        conn.close()




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


@bp.route('/admin/reports', methods=['GET'])
@jwt_required()
def sales_reports():
    """Fetch all sales reports and pass to admin/sales.html"""
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Monthly Sales Breakdown
    cursor.execute("""
        SELECT DATE_FORMAT(booking_time, '%Y-%m') AS month, 
               SUM(fp.price * b.seats) AS total_sales
        FROM bookings b
        JOIN flight_prices fp ON b.flight_id = fp.id
        WHERE b.payment_status = 'paid'
        GROUP BY month
        ORDER BY month DESC
    """)
    monthly_sales = cursor.fetchall()

    # Sales per Journey
    cursor.execute("""
        SELECT fp.departure, fp.destination, 
               SUM(fp.price * b.seats) AS total_sales, 
               COUNT(b.booking_id) AS total_bookings
        FROM bookings b
        JOIN flight_prices fp ON b.flight_id = fp.id
        WHERE b.payment_status = 'paid'
        GROUP BY fp.departure, fp.destination
        ORDER BY total_sales DESC
    """)
    sales_per_journey = cursor.fetchall()

    # Top Customers
    cursor.execute("""
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
    """)
    top_customers = cursor.fetchall()

    # Profitable Routes
    cursor.execute("""
        SELECT fp.departure, fp.destination, 
               SUM(fp.price * b.seats) AS revenue,
               COUNT(b.booking_id) AS total_bookings
        FROM bookings b
        JOIN flight_prices fp ON b.flight_id = fp.id
        WHERE b.payment_status = 'paid'
        GROUP BY fp.departure, fp.destination
        HAVING revenue > 5000
        ORDER BY revenue DESC
    """)
    profitable_routes = cursor.fetchall()

    # Loss-Making Routes
    cursor.execute("""
        SELECT fp.departure, fp.destination, 
               SUM(fp.price * b.seats) AS revenue,
               COUNT(b.booking_id) AS total_bookings
        FROM bookings b
        JOIN flight_prices fp ON b.flight_id = fp.id
        WHERE b.payment_status = 'paid'
        GROUP BY fp.departure, fp.destination
        HAVING revenue < 1000
        ORDER BY revenue ASC
    """)
    loss_routes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin/sales.html",
        monthly_sales=monthly_sales,
        sales_per_journey=sales_per_journey,
        top_customers=top_customers,
        profitable_routes=profitable_routes,
        loss_routes=loss_routes
    )



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
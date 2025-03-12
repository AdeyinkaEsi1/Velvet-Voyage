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

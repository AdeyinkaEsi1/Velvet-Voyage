from flask import Blueprint, request, jsonify, render_template
import mysql.connector
from config import Config
bp = Blueprint('login', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )
    
@bp.route('/')
def login():
    return render_template("login.html")

from flask import Blueprint, redirect, request, jsonify, render_template, url_for
import mysql.connector
from config import Config

bp = Blueprint('main', __name__)

def get_db_connection():
    conn = mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )
    return conn

@bp.route('/')
def home():
    error_message = request.args.get("error")
    return render_template("index.html", error=error_message)
#  {% if error %}
#         <div style="color: red; font-weight: bold;">
#             {{ error }}
#         </div>
#     {% endif %}
    

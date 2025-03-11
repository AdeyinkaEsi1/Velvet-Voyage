from flask import Blueprint, redirect, request, jsonify, render_template, url_for
import mysql.connector
from config import Config
from flask import session

bp = Blueprint('main', __name__)

def get_db_connection():
    conn = mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )
    return conn




@bp.route('/', methods=["GET"])
def home():
    return render_template("home/index.html")

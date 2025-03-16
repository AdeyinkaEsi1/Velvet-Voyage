from flask import Blueprint, render_template
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


@bp.route('/', methods=["GET"])
def home():
    return render_template("index.html")


@bp.route('/contact', methods=["GET"])
def contact():
    return render_template("contact.html")


@bp.route('/about', methods=["GET"])
def about():
    return render_template("about-us.html")



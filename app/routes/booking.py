from flask import Blueprint, request, jsonify, render_template

bp = Blueprint('booking', __name__)

@bp.route('/')
def booking_list():
    # return render_template('booking.html', title="Flights", username="Hamid")
    return jsonify({'flights': 'list of dddd'})

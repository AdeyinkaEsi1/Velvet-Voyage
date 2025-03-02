from flask import Blueprint, request, jsonify, render_template

bp = Blueprint('flights_bp', __name__)

@bp.route('/')
def flight_list():
    return render_template('flights.html', title="Flights", username="Hamid")
    # return jsonify({'flights': 'list of flights'})


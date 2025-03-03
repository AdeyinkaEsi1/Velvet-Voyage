from flask import Blueprint, request, jsonify, render_template

bp = Blueprint('signup', __name__)

@bp.route('/')
def signup():
    return render_template('signup.html', title="Auth", username="Hamid")
    # return jsonify({'flights': 'list of auths'})

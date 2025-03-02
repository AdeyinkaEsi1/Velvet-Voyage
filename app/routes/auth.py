from flask import Blueprint, request, jsonify, render_template

bp = Blueprint('auth', __name__)

@bp.route('/')
def auth_list():
    return render_template('auth.html', title="Auth", username="Hamid")
    # return jsonify({'flights': 'list of auths'})

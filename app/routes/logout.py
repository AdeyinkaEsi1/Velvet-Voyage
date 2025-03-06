from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import get_jwt, jwt_required, unset_access_cookies
from app import revoked_tokens

bp = Blueprint('logout', __name__)


@bp.route('/', methods=['POST'])
@jwt_required()
def logout():
    print("Cookies at logout:", request.cookies)
    response = make_response(jsonify({"message": "Successfully logged out"}))
    response.set_cookie("access_token_cookie", "", expires=0, httponly=True, secure=True, samesite='Lax')
    return response, 200

    # unset_access_cookies(response)
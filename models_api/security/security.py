from flask import jsonify
from flask_restful import request
import jwt
from functools import wraps
from flask import current_app

def token_required(f):
    @wraps(f)
    def decorated(model, *args, **kwargs):
        token = request.headers.get('token')

        if not token:
            return 'TokenIsRequired', 403        
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], 
                                 algorithms = 'HS256')
            method = request.method.lower()
            return f(model, *args, **kwargs)
        except Exception as e:
            return 'InvalidToken', 403
    return decorated
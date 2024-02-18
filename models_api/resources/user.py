from flask import jsonify, session
from flask_restful import Resource, reqparse, request
from flask import current_app
import json
import bcrypt
import pickle
import jwt
import datetime

class User(Resource):
    atributos = reqparse.RequestParser()
    atributos.add_argument('login', type=str)
    atributos.add_argument('password', type=str)

    def post(self):
        _SECRET_KEY = current_app.config['SECRET_KEY']
        _LIMIT = datetime.timedelta(minutes=30)
        request_json = request.get_json()
        login = request_json['login']
        password = request_json['password']
        
        file = open('users.json')
        users = json.load(file)
        file.close()

        if login in users["login"]:
            encrypted = User.get_hash()
            if User.authenticate(password, encrypted):
                session['logged_in'] = True
                token = jwt.encode({'user': login,
                                    'expiration': (datetime.datetime.utcnow() + _LIMIT).isoformat(),
                                    'exp': datetime.datetime.utcnow() + _LIMIT}, 
                                    _SECRET_KEY)
                return jsonify({'AccessToken': token})
        return 'IncorrectCredentials', 401

    @classmethod
    def get_hash(cls):
        hash = None
        with open('auth', 'rb') as f:
            try:
                hash = pickle.load(f)
            except EOFError:
                pass
        return hash

    @classmethod
    def authenticate(cls, password, encrypted):
        return bcrypt.hashpw(password.encode('utf8'), encrypted) == encrypted
            
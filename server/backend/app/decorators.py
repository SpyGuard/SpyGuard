
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import request, jsonify
from flask import current_app as app
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from app.utils import read_config
import jwt
import hashlib

auth = HTTPBasicAuth()


@auth.verify_password
def check_creds(user, password):
    """
        Check the credentials
        :return: :bool: if the authentication succeed.
    """
    if user == read_config(("backend", "login")) and check_password(password):
        return True


def check_password(password):
    """
        Password hashes comparison (submitted and the config one)
        :return: True if there is a match between the two hases
    """
    if read_config(("backend", "password")) == hashlib.sha256(password.encode()).hexdigest():
        return True


def require_header_token(f):
    """
        Check the JWT token validity in POST requests.
        :return: decorated method
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = request.headers['X-Token']
            jwt.decode(token, app.config["SECRET_KEY"], "HS256")
            return f(*args, **kwargs)
        except:
            return jsonify({"message": "JWT verification failed"})
    return decorated


def require_get_token(f):
    """
        Check the JWT token validity in GET requests.
        :return: decorated method
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = request.args.get("token")
            jwt.decode(token, app.config["SECRET_KEY"], "HS256")
            return f(*args, **kwargs)
        except:
            return jsonify({"message": "JWT verification failed"})
    return decorated

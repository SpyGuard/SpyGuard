#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import jsonify, Blueprint
from app.classes.update import Update
from app.decorators import require_header_token

update_bp = Blueprint("update", __name__)

@update_bp.route("/check", methods=["GET"])
@require_header_token
def check():
    """ Check the presence of new version """
    return jsonify(Update().check_version())

@update_bp.route("/get-version", methods=["GET"])
def get_version():
    """ Check the current version """
    return jsonify(Update().get_current_version())

@update_bp.route("/process", methods=["GET"])
@require_header_token
def process():
    """ Check the presence of new version """
    return jsonify(Update().update_instance())
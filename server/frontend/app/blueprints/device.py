#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import jsonify, Blueprint
from app.classes.device import Device

device_bp = Blueprint("device", __name__)


@device_bp.route("/get/<token>", methods=["GET"])
def api_device_get(token):
    """ Get device assets """
    return jsonify(Device(token).get())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import jsonify, Blueprint
from app.classes.capture import Capture

capture = Capture()
capture_bp = Blueprint("capture", __name__)


@capture_bp.route("/start", methods=["GET"])
def api_capture_start():
    """ Start the capture """
    return jsonify(capture.start_capture())


@capture_bp.route("/stop", methods=["GET"])
def api_capture_stop():
    """ Stop the capture """
    return jsonify(capture.stop_capture())


@capture_bp.route("/stats", methods=["GET"])
def api_capture_stats():
    """ Stop the capture """
    return jsonify(capture.get_capture_stats())

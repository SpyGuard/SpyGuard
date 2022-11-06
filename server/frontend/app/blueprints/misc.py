#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess as sp
from flask import Blueprint, jsonify
from app.utils import *
from app.classes.capture import stop_monitoring
import re
import sys
import os

misc_bp = Blueprint("misc", __name__)


@misc_bp.route("/delete-captures", methods=["GET"])
def api_delete_captures():
    """
        Delete the zombies capture folders (if any)
    """
    if delete_captures() and stop_monitoring():
        return jsonify({"message": "Captures deleted", "status": True})
    else:
        return jsonify({"message": "Issue while removing captures", "status": False})


@misc_bp.route("/reboot", methods=["GET"])
def api_reboot():
    """
        Reboot the device
    """
    if read_config(("frontend", "reboot_option")):
        sp.Popen("shutdown -r now", shell=True)
        return jsonify({"mesage": "Let's reboot."})
    else:
        return jsonify({"message": "Option disabled", "status": False})


@misc_bp.route("/quit", methods=["GET"])
def api_quit():
    """
        Quit the interface (Chromium browser)
    """
    if read_config(("frontend", "quit_option")):
        sp.Popen('pkill -INT -f "chromium-browser"', shell=True)
        return jsonify({"message": "Let's quit", "status": True})
    else:
        return jsonify({"message": "Option disabled", "status": False})


@misc_bp.route("/shutdown", methods=["GET"])
def api_shutdown():
    """
        Reboot the device
    """
    if read_config(("frontend", "shutdown_option")):
        sp.Popen("shutdown -h now", shell=True)
        return jsonify({"message": "Let's shutdown", "status": True})
    else:
        return jsonify({"message": "Option disabled", "status": False})


@misc_bp.route("/config", methods=["GET"])
def get_config():
    """
        Get configuration keys relative to the GUI
    """
    return jsonify({
        "battery_level" : get_battery_level(),
        "wifi_level" : get_wifi_level(),
        "virtual_keyboard": read_config(("frontend", "virtual_keyboard")),
        "download_links": read_config(("frontend", "download_links")),
        "sparklines": read_config(("frontend", "sparklines")),
        "shutdown_option": read_config(("frontend", "shutdown_option")),
        "backend_option": read_config(("frontend", "backend_option")),
        "remote_backend" : read_config(("backend", "remote_access")),
        "iface_out": read_config(("network", "out")),
        "user_lang": read_config(("frontend", "user_lang")),
        "choose_net": read_config(("frontend", "choose_net")),
        "slideshow":  read_config(("frontend", "slideshow")),
        "iocs_number" : get_iocs_number()
    })

@misc_bp.route("/battery", methods=["GET"])
def battery_level():
    """
        Return the battery level
    """
    return jsonify({
        "battery_level" : get_battery_level()
    })

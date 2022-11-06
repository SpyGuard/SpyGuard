#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request
from app.classes.save import Save
from app.classes.device import Device

save = Save()
save_bp = Blueprint("save", __name__)


@save_bp.route("/usb-check", methods=["GET"])
def api_usb_list():
    """ List connected usb devices """
    return save.usb_check()


@save_bp.route("/save-capture/<token>/<method>", methods=["GET"])
def api_save_capture(token, method):
    """ Save the capture on the USB or for download """
    return save.save_capture(token, method)

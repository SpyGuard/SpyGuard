#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify
from app.decorators import *
from app.classes.config import Config
from app.utils import get_device_uuid
import sys

config_bp = Blueprint("config", __name__)
config = Config()


@config_bp.route('/switch/<cat>/<key>', methods=['GET'])
@require_header_token
def switch(cat, key):
    """Switch the Boolean value of a configuration key.

    Args:
        cat (str): configuration category
        key (key): configuration key

    Returns:
        dict: operation status
    """
    try:
        value = config.read_config((cat, key))
        if value:
            config.write_config(cat, key, False)
            res = {"status": True,
                   "message": "Key switched to false"}
        else:
            config.write_config(cat, key, True)
            res = {"status": True,
                   "message": "Key switched to true"}
    except:
        res = {"status": True,
               "message": "Issue while changing value"}

    return jsonify(res)


@config_bp.route('/ioc-type/add/<tag>', methods=['GET'])
@require_header_token
def ioc_type_add(tag):
    """Add an IOC type - defined via its tag - in the 
    configuration file for detection.

    Args:
        tag (str): IOC tag

    Returns:
        dict: operation status
    """
    return jsonify(config.ioc_type_add(tag))


@config_bp.route('/ioc-type/delete/<tag>', methods=['GET'])
@require_header_token
def ioc_type_delete(tag):
    """Delete an IOC type - defined via its tag - in the 
    configuration file for detection.

    Args:
        tag (str): IOC tag

    Returns:
        dict: operation status
    """
    return jsonify(config.ioc_type_delete(tag))


@config_bp.route('/edit/<cat>/<key>/<path:value>', methods=['GET'])
@require_header_token
def edit(cat, key, value):
    """Edit the string (or array) value of a configuration key.

    Args:
        cat (str): configuration category
        key (str): configuration key
        value (any): configuration value
    Returns:
        dict: operation status
    """
    return jsonify(config.write_config(cat, key, value))
    

@config_bp.route('/db/export', methods=['GET'])
@require_get_token
def export_db():
    """Export the database.

    Returns:
        dict: the raw database
    """
    return config.export_db()


@config_bp.route('/db/import', methods=['POST'])
@require_header_token
def import_db():
    """Import a database via Flash methods 
    and replace the existant.

    Returns:
        dict: operation status
    """
    try:
        f = request.files["file"]
        assert f.read(15) == b"SQLite format 3"
        d = "/".join(sys.path[0].split("/")[:-2])
        f.save("/{}/database.sqlite3".format(d))
        res = {"status": True,
               "message": "Database updated"}
    except:
        res = {"status": False,
               "message": "Error while database upload"}
    return jsonify(res)


@config_bp.route('/list', methods=['GET'])
def list():
    """List key, values of the configuration

    Returns:
        dict: configuration content
    """
    res = config.export_config()
    res["backend"]["password"] = ""
    res["device_uuid"] = get_device_uuid()
    return jsonify(res)

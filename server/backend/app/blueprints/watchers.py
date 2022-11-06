#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request
from app.decorators import require_header_token
from app.classes.watchers import Watcher

import json

watchers_bp = Blueprint("watchers", __name__)
watcher = Watcher()

@watchers_bp.route('/add', methods=['POST'])
@require_header_token
def add_instance():
    """
        Parse and add a watcher instance.
        :return: status of the operation in JSON
    """
    data = json.loads(request.data)
    res = watcher.add_instance(data["data"]["instance"])
    return jsonify(res)

@watchers_bp.route('/delete/<watcher_id>', methods=['GET'])
@require_header_token
def delete_instance(watcher_id):
    """
        Delete a watcher by its id.
        :return: status of the operation in JSON
    """
    res = watcher.delete_instance(watcher_id)
    return jsonify(res)

@watchers_bp.route('/get_all', methods=['GET'])
@require_header_token
def get_all():
    """
        Retreive a list of all watchers.
        :return: list of watcher instances in JSON.
    """
    res = watcher.get_instances()
    return jsonify({"results": [i for i in res]})

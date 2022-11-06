#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import db
from app.db.models import Whitelist
from sqlalchemy.sql import exists
from app.definitions import definitions
from flask import escape
import re
import time


class WhiteList(object):
    def __init__(self):
        return None

    @staticmethod
    def add(elem_type, elem_value, source):
        """
            Parse and add an element to be whitelisted.
            :return: status of the operation in a dict
        """
        elem_value = elem_value.lower()
        elem_valid = False

        if db.session.query(exists().where(Whitelist.element == elem_value)).scalar():
            return {"status": False,
                    "message": "Element already whitelisted",
                    "element": escape(elem_value)}
        elif elem_type == "unknown":
            for t in definitions["whitelist_types"]:
                if t["regex"] and t["auto"]:
                    if re.match(t["regex"], elem_value):
                        elem_type = t["type"]
                        elem_valid = True
                        break
        elif elem_type in [t["type"] for t in definitions["whitelist_types"]]:
            for t in definitions["whitelist_types"]:
                if t["type"] == elem_type and t["regex"]:
                    if re.match(t["regex"], elem_value):
                        elem_valid = True
                        break
        if elem_valid:
            added_on = int(time.time())
            db.session.add(Whitelist(elem_value, elem_type, source, added_on))
            db.session.commit()
            return {"status": True,
                    "message": "Element whitelisted",
                    "element": escape(elem_value)}
        else:
            return {"status": False,
                    "message": "Wrong element format",
                    "element": escape(elem_value)}

    @staticmethod
    def delete(elem_id):
        """
            Delete an element by its id in the database.
            :return: status of the operation in a dict
        """
        if db.session.query(exists().where(Whitelist.id == elem_id)).scalar():
            db.session.query(Whitelist).filter_by(id=elem_id).delete()
            db.session.commit()
            return {"status": True,
                    "message": "Element deleted"}
        else:
            return {"status": False,
                    "message": "Element not found"}

    @staticmethod
    def delete_by_value(elem_value):
        """
            Delete an element by its value in the database.
            :return: status of the operation in a dict
        """
        if db.session.query(exists().where(Whitelist.element == elem_value)).scalar():
            db.session.query(Whitelist).filter_by(element=elem_value).delete()
            db.session.commit()
            return {"status": True,
                    "message": "Element deleted"}
        else:
            return {"status": False,
                    "message": "Element not found"}

    @staticmethod
    def search(element):
        """
            Search elements in the database.
            :return: generator containing elements.
        """
        elems = db.session.query(Whitelist).filter(
            Whitelist.element.like(element.replace("*", "%"))).all()
        for elem in elems:
            elem = elem.__dict__
            yield {"id": elem["id"],
                   "type": elem["type"],
                   "element": elem["element"]}

    @staticmethod
    def get_types():
        """
            Get types of whitelisted elements.
            :return: generator containing types.
        """
        for t in definitions["whitelist_types"]:
            yield {"type": t["type"], "name": t["name"]}

    @staticmethod
    def get_all():
        """
            Retrieve all whitelisted elements.
            :return: generator containing elements.
        """
        for elem in db.session.query(Whitelist).all():
            elem = elem.__dict__
            yield {"type": elem["type"],
                   "element": elem["element"]}

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import db
from app.db.models import Ioc
from sqlalchemy.sql import exists
from app.definitions import definitions
from markupsafe import escape
import re
import time


class IOCs(object):
    def __init__(self):
        return None

    @staticmethod
    def add(ioc_type, ioc_tag, ioc_tlp, ioc_value, source):
        """
            Parse and add an IOC to the database.
            :return: status of the operation in JSON
        """

        ioc_value = ioc_value.lower() if ioc_type != "snort" else ioc_value
        ioc_valid = False
        if db.session.query(exists().where(Ioc.value == ioc_value)).scalar():
            return {"status": False,
                    "message": "IOC already exists",
                    "ioc": escape(ioc_value)}
        elif ioc_tlp in ["white", "green", "amber", "red"]:
            if ioc_type == "unknown":
                for t in definitions["iocs_types"]:
                    if t["regex"] and t["auto"]:
                        if re.match(t["regex"], ioc_value):
                            ioc_type = t["type"]
                            ioc_valid = True
            elif ioc_type in [t["type"] for t in definitions["iocs_types"]]:
                for t in definitions["iocs_types"]:
                    if t["type"] == ioc_type and t["regex"]:
                        if re.match(t["regex"], ioc_value):
                            ioc_valid = True
                            break
                    elif t["type"] == "snort" and ioc_value[0:6] == "alert ":
                        ioc_valid = True
                        break
            else:
                return {"status": True,
                        "message": "Wrong IOC type",
                        "ioc": escape(ioc_value),
                        "type": escape(ioc_type)}

            if ioc_valid:
                added_on = int(time.time())
                db.session.add(Ioc(ioc_value, ioc_type, ioc_tlp,
                                   ioc_tag, source, added_on))
                db.session.commit()
                return {"status": True,
                        "message": "IOC added",
                        "ioc": escape(ioc_value),
                        "type": escape(ioc_type),
                        "tlp": escape(ioc_tlp),
                        "tag": escape(ioc_tag),
                        "source": escape(source),
                        "added_on": escape(added_on)}
            else:
                return {"status": False,
                        "message": "Wrong IOC format",
                        "ioc": escape(ioc_value)}
        else:
            return {"status": False,
                    "message": "Wrong IOC TLP",
                    "ioc": escape(ioc_value),
                    "type": escape(ioc_tlp)}

    @staticmethod
    def delete(ioc_id):
        """
            Delete an IOC by its id in the database.
            :return: status of the operation in JSON
        """
        if db.session.query(exists().where(Ioc.id == ioc_id)).scalar():
            db.session.query(Ioc).filter_by(id=ioc_id).delete()
            db.session.commit()
            return {"status": True,
                    "message": "IOC deleted"}
        else:
            return {"status": False,
                    "message": "IOC not found"}

    @staticmethod
    def delete_by_value(ioc_value):
        """
            Delete an IOC by its value in the database.
            :return: status of the operation in JSON
        """
        if db.session.query(exists().where(Ioc.value == ioc_value)).scalar():
            db.session.query(Ioc).filter_by(value=ioc_value).delete()
            db.session.commit()
            return {"status": True,
                    "message": "IOC deleted"}
        else:
            return {"status": False,
                    "message": "IOC not found"}

    @staticmethod
    def search(term):
        """
            Search IOCs in the database.
            :return: generator of results.
        """
        iocs = db.session.query(Ioc).filter(
            Ioc.value.like(term.replace("*", "%"))).all()
        for ioc in iocs:
            ioc = ioc.__dict__
            yield {"id": ioc["id"],
                   "type": ioc["type"],
                   "tag": ioc["tag"],
                   "tlp": ioc["tlp"],
                   "value": ioc["value"],
                   "source": ioc["source"]}

    @staticmethod
    def get_types():
        """
            Retreive a list of IOCs types.
            :return: generator of iocs types.
        """
        for t in definitions["iocs_types"]:
            yield {"type": t["type"],
                   "name": t["name"]}

    @staticmethod
    def get_tags():
        """
            Retreive a list of IOCs tags.
            :return: generator of iocs tags.
        """
        rtn = [i["tag"] for i in definitions["iocs_tags"]]
        for ioc in db.session.query(Ioc).all():
            ioc = ioc.__dict__
            tag = ioc["tag"]
            if tag not in rtn:
                rtn.append(tag)
        return list(set(rtn))

    @staticmethod
    def get_all():
        """
            Get all IOCs from the database
            :return: generator of the records.
        """
        for ioc in db.session.query(Ioc).all():
            ioc = ioc.__dict__
            yield {"id": ioc["id"],
                   "type": ioc["type"],
                   "tag": ioc["tag"],
                   "tlp": ioc["tlp"],
                   "value": ioc["value"]}

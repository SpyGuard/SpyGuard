#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import sys
import io
import os
import re
import hashlib
import subprocess as sp
from functools import reduce
from flask import send_file


class Config(object):
    def __init__(self):
        self.dir = "/".join(sys.path[0].split("/")[:-2])
        return None

    def read_config(self, path):
        """
            Read a single value from the configuration
            :return: value (it can be any type)
        """
        config = yaml.load(
            open(os.path.join(self.dir, "config.yaml"), "r"), Loader=yaml.SafeLoader)
        return reduce(dict.get, path, config)

    def export_config(self):
        """
            Export the configuration
            :return: dict (configuration content)
        """
        config = yaml.load(open(os.path.join(self.dir, "config.yaml"), "r"), Loader=yaml.SafeLoader)
        config["ifaces_in"] = self.get_ifaces_in()
        config["ifaces_out"] = self.get_ifaces_out()
        config["analysis"]["indicators_types"] = config["analysis"]["indicators_types"] if config["analysis"]["indicators_types"] else []
        return config

    def ioc_type_add(self, tag):
        """Add an IOC type to the config file

        Args:
            tag (str): IOC type.
        """
        config = yaml.load(open(os.path.join(self.dir, "config.yaml"), "r"), Loader=yaml.SafeLoader)
        config["analysis"]["indicators_types"].append(tag)
        with open(os.path.join(self.dir, "config.yaml"), "w") as yaml_file:
            yaml_file.write(yaml.dump(config, default_flow_style=False))
            return {"status": True,
                    "message": "Configuration updated"}

    def ioc_type_delete(self, tag):
        """Delete an IOC type to the config file

        Args:
            tag (str): IOC type.
        """
        config = yaml.load(open(os.path.join(self.dir, "config.yaml"), "r"), Loader=yaml.SafeLoader)
        config["analysis"]["indicators_types"].remove(tag)
        with open(os.path.join(self.dir, "config.yaml"), "w") as yaml_file:
            yaml_file.write(yaml.dump(config, default_flow_style=False))
            return {"status": True,
                    "message": "Configuration updated"}

    def write_config(self, cat, key, value) -> dict:
        """Write a value in the configuration

        Args:
            cat (str): category
            key (str): key 
            value (str): value to write

        Returns:
            dict: status of the operation.
        """

        config = yaml.load(open(os.path.join(self.dir, "config.yaml"), "r"), Loader=yaml.SafeLoader)

        # Some checks prior configuration changes.
        if cat not in config:
            return {"status": False,
                    "message": "Wrong category specified"}

        if key not in config[cat]:
            return {"status": False,
                    "message": "Wrong key specified"}

        # Changes for network interfaces.
        if cat == "network" and key in ["in", "out"]:
            if re.match("^(wlan[0-9]|wl[a-z0-9]{2,20})$", value):
                if key == "in":
                    config[cat][key] = value
                if key == "out":
                    config[cat][key] = value
            elif re.match("^(eth[0-9]|en[a-z0-9]{2,20}|ww[a-z0-9]{2,20}|lo)$", value) and key == "out":
                config[cat][key] = value
            else:
                return {"status": False,
                        "message": "Wrong value specified"}

        # Changes for network SSIDs.
        elif cat == "network" and key == "ssids":
            ssids = list(set(value.split("|"))) if "|" in value else [value]
            if len(ssids):
                config[cat][key] = ssids

        # Changes for backend password.
        elif cat == "backend" and key == "password":
            config[cat][key] = self.make_password(value)

        # Changes for anything not specified.
        # Warning: can break your config if you play with it (eg. arrays, ints & bools).
        else:
            if isinstance(value, bool):
                config[cat][key] = value
            elif len(value):
                config[cat][key] = value

        with open(os.path.join(self.dir, "config.yaml"), "w") as yaml_file:
            yaml_file.write(yaml.dump(config, default_flow_style=False))
            sp.Popen(["systemctl", "restart", "spyguard-frontend"]).wait()
            return {"status": True,
                    "message": "Configuration updated"}

    def make_password(self, clear_text):
        """Make a simple sha256 password hash without salt.

        Args:
            clear_text (str): clear text password

        Returns:
            string: hexdigest of the password sha256 hash.
        """
        return hashlib.sha256(clear_text.encode()).hexdigest()

    def export_db(self):
        """Propose the database to download.

        Returns:
            Response: Flask Response.
        """
        with open(os.path.join(self.dir, "database.sqlite3"), "rb") as f:
            return send_file(
                io.BytesIO(f.read()),
                mimetype="application/octet-stream",
                as_attachment=True,
                attachment_filename='spyguard-export-db.sqlite')

    def get_ifaces_in(self) -> list:
        """ List the wireless interfaces which can be 
        used for the access point

        Returns:
            list: List of available network interfaces
        """
        try:
            return [i for i in os.listdir("/sys/class/net/") if i.startswith("wl")]
        except:
            return ["No wireless interface"]

    def get_ifaces_out(self) -> list:
        """ List the network interfaces which can be 
        used to access to Internet.

        Returns:
            list: List of available network interfaces
        """
        try:
            ifaces = ("wl", "et", "en", "ww", "lo")
            return [i for i in os.listdir("/sys/class/net/") if i.startswith(ifaces)]
        except:
            return ["No network interfaces"]


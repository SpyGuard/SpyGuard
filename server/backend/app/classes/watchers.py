#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from typing import Iterator

import requests
import yaml
from flask import escape
from sqlalchemy.sql import exists


class Watcher(object):
    def __init__(self):
        self.dir = "/".join(sys.path[0].split("/")[:-2])
        self.watchers = [w for w in self.get_watchers()]
        return None

    def add_instance(self, instance) -> dict:
        """Add a watcher instance.

        Args:
            instance (dict): Instance to add.

        Returns:
            dict: operation status.
        """

        w = { "name" : instance["name"],
              "url" : instance["url"],
              "type" : instance["type"] } 

        if w["url"] not in [w["url"] for w in self.watchers]:
            self.watchers.append(w)
            if self.update_watchers():
                return {"status": True,
                        "message": "Watcher added"}
        else:
            return {"status": False,
                    "message": "This watcher already exists"}

    def delete_instance(self, watcher_id) -> dict:
        """Delete a watcher defined by its id

        Args:
            watcher_id (str): watcher id.

        Returns:
            dict: operation status.
        """
        self.watchers.pop(int(watcher_id))
        if self.update_watchers():
            return {"status": True,
                    "message": "Watcher deleted"}
        else:
            return {"status": False,
                    "message": "Watcher not found"}

    def update_watchers(self):
        """Update the watchers files.

        Returns:
            bool: True if successful
        """
        try:
            dir = "/".join(sys.path[0].split("/")[:-2])
            watchers = yaml.load(open(os.path.join(dir, "watchers.yaml"), "r"), Loader=yaml.SafeLoader)
            with open(os.path.join(dir, "watchers.yaml"), "w") as yaml_file:
                yaml_file.write(yaml.dump({ "watchers" : self.watchers }, default_flow_style=False))
                return True
        except:
            return False

    def get_watchers(self) -> Iterator[list]:
        """Get the watcher instances from the yaml 
        watchers file

        Yields:
            Iterator[list]: watchers list
        """
        dir = "/".join(sys.path[0].split("/")[:-2])
        watchers = yaml.load(open(os.path.join(dir, "watchers.yaml"), "r"), Loader=yaml.SafeLoader)
        for watcher in watchers["watchers"]:
            yield watcher

    def get_instances(self) -> Iterator[list]:
        """Get the watcher instances from the yaml 
        watchers file

        Yields:
            Iterator[list]: watchers list
        """
        for id, watcher in enumerate(self.get_watchers()):
            watcher["id"] = id
            watcher["status"] = self.get_watcher_status(watcher["url"])
            yield watcher

    def get_watcher_status(self, url):
        """Get the status of a watcher by controling 
        its HTTP status code. 

        Args:
            url (string): The watcher URL

        Returns:
            bool: True if OK.
        """

        res = requests.get(url, verify=False)
        if res.status_code == 200:
            return True

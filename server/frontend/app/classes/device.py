#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmath import rect
import subprocess as sp
from app.utils import read_config

import json
import os
import re

class Device(object):

    def __init__(self, token):
        self.iface_in = read_config(("network", "in"))
        self.token = token if re.match(r"[A-F0-9]{8}", token) else None
        return None

    def get(self) -> dict:
        """Get the device properties (such as Mac address, name, IP etc.)
           By reading the device.json file if exists. Or reading the leases
           files and writing the result into device.json. 

        Returns:
            dict: device infos.
        """
        if not os.path.isfile("/tmp/{}/assets/device.json".format(self.token)):
            device = self.read_leases()
            if device["status"] != False:
                with open("/tmp/{}/assets/device.json".format(self.token), "w") as f:
                    f.write(json.dumps(device))
        else:
            with open("/tmp/{}/assets/device.json".format(self.token)) as f:
                device = json.load(f)
        return device

    def read_leases(self) -> dict:
        """Get the first connected device to the generated 
        networks by using ARP.

        Returns:
            dict: connected device.
        """

        sh = sp.Popen(["arp"], stdout=sp.PIPE, stderr=sp.PIPE)
        sh = sh.communicate()

        for line in sh[0].splitlines():
            line = line.decode("utf8")
            if self.iface_in in line:
                rec = [x for x in line.split(" ") if x]
                if rec[-1] == self.iface_in and rec[1] == "ether":
                    return {
                        "status": True,
                        "name": rec[2],
                        "ip_address": rec[0],
                        "mac_address": rec[2]
                    }
        else:
            return {"status": False,
                    "message": "Device not connected"}

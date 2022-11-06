#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess as sp
import json
import sys
import re
import os


class Analysis(object):

    def __init__(self, token):
        self.token = token if re.match(r"[A-F0-9]{8}", token) else None

    def start(self) -> dict:
        """Start the analysis of the captured communication by lauching
        analysis.py with the capture token as a paramater.

        Returns:
            dict: operation status
        """

        if self.token is not None:
            parent = "/".join(sys.path[0].split("/")[:-2])
            sp.Popen(
                [sys.executable, "{}/analysis/analysis.py".format(parent), "/tmp/{}".format(self.token)])
            return {"status": True,
                    "message": "Analysis started",
                    "token": self.token}
        else:
            return {"status": False,
                    "message": "Bad token provided",
                    "token": "null"}

    def get_report(self) -> dict:
        """Generate a small json report of the analysis
        containing the alerts and the device properties.

        Returns:
            dict: alerts, pcap and device info.
        """

        device, alerts, pcap = {}, {}, {}

        # Getting device configuration.
        if os.path.isfile("/tmp/{}/assets/device.json".format(self.token)):
            with open("/tmp/{}/assets/device.json".format(self.token), "r") as f:
                device = json.load(f)

        # Getting pcap infos.
        if os.path.isfile("/tmp/{}/assets/capinfos.json".format(self.token)):
            with open("/tmp/{}/assets/capinfos.json".format(self.token), "r") as f:
                pcap = json.load(f)

        # Getting alerts configuration.
        if os.path.isfile("/tmp/{}/assets/alerts.json".format(self.token)):
            with open("/tmp/{}/assets/alerts.json".format(self.token), "r") as f:
                alerts = json.load(f)

        # Getting detection methods.
        if os.path.isfile("/tmp/{}/assets/detection_methods.json".format(self.token)):
            with open("/tmp/{}/assets/detection_methods.json".format(self.token), "r") as f:
                methods = json.load(f)

        # Getting records.
        if os.path.isfile("/tmp/{}/assets/records.json".format(self.token)):
            with open("/tmp/{}/assets/records.json".format(self.token), "r") as f:
                records = json.load(f)

        if device != {} and alerts != {}:
            return {"alerts": alerts,
                    "device": device,
                    "methods": methods,
                    "pcap": pcap, 
                    "records": records}
        else:
            return {"message": "No report yet"}

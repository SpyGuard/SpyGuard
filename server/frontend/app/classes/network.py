#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess as sp
import netifaces as ni
import requests
import re
import qrcode
import base64
import random
import requests
from app.utils import read_config

from io import BytesIO


class Network(object):

    def __init__(self):
        self.AP_SSID = False
        self.AP_PASS = False
        self.iface_out = read_config(("network", "out"))
        self.iface_in = read_config(("network", "in"))
        self.random_choice_alphabet = "abcdef1234567890"


    def check_status(self) -> dict:
        """The method check_status check the IP addressing of the connected interface
        and return its associated IP.

        Returns:
            dict: contains the network context.
        """

        ctx = { "internet": self.check_internet() }

        for iface in ni.interfaces():
            if iface != self.iface_in and iface.startswith(("wl", "en", "et")):
                addrs = ni.ifaddresses(iface)
                try:
                    ctx["ip_out"] = addrs[ni.AF_INET][0]["addr"]
                except:
                    ctx["ip_out"] = "Not connected"
        return ctx


    def wifi_list_networks(self) -> dict:
        """List the available wifi networks by using nmcli

        Returns:
            dict: list of available networks.
        """

        networks = []
        if self.iface_out.startswith("wl"):
            sh = sp.Popen(["nmcli", "-f", "SSID,SIGNAL", "dev", "wifi", "list", "ifname", self.iface_out], stdout=sp.PIPE, stderr=sp.PIPE)
            sh = sh.communicate()
        
            for network in [n.decode("utf8") for n in sh[0].splitlines()][1:]:
                name = network.strip()[:-3].strip()
                signal = network.strip()[-3:].strip()
                if name not in [n["name"] for n in networks] and name != "--":
                    networks.append({"name" : name, "signal" : int(signal) })
        return { "networks": networks }
 

    def wifi_setup(self, ssid, password) -> dict:
        """Connect to a WiFi network by using nmcli

        Args:
            ssid (str): Network SSID
            password (str): Network password

        Returns:
            dict: operation status
        """

        if len(password) >= 8 and len(ssid):
            sh = sp.Popen(["nmcli", "dev", "wifi", "connect", ssid, "password", password, "ifname", self.iface_out], stdout=sp.PIPE, stderr=sp.PIPE)
            sh = sh.communicate()

            if re.match(".*[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}.*", sh[0].decode('utf8')):
                return {"status": True,
                        "message": "Wifi connected"}
            else:
                return {"status": False,
                        "message": "Wifi not connected"}
        else:
            return {"status": False,
                    "message": "Empty SSID or/and password length less than 8 chars."}

    def start_hotspot(self) -> dict:
        """Generates an Access Point by using nmcli and provide to 
        the GUI the associated ssid, password and qrcode.

        Returns:
            dict: hostpost description
        """

        self.delete_hotspot()
        
        try:
            if read_config(("network", "tokenized_ssids")):
                token = "".join([random.choice(self.random_choice_alphabet) for i in range(4)])
                self.AP_SSID = random.choice(read_config(("network", "ssids"))) + "-" + token
            else:
                self.AP_SSID = random.choice(read_config(("network", "ssids")))
        except:
            token = "".join([random.choice(self.random_choice_alphabet) for i in range(4)])
            self.AP_SSID = "wifi-" + token

        self.AP_PASS = "".join([random.choice(self.random_choice_alphabet) for i in range(8)])

        sp.Popen(["nmcli", "con", "add", "type", "wifi", "ifname", self.iface_in, "con-name", self.AP_SSID, "autoconnect", "yes", "ssid", self.AP_SSID]).wait()
        sp.Popen(["nmcli", "con", "modify", self.AP_SSID, "802-11-wireless.mode", "ap", "802-11-wireless.band", "bg", "ipv4.method", "shared"]).wait()
        sp.Popen(["nmcli", "con", "modify", self.AP_SSID, "wifi-sec.key-mgmt", "wpa-psk", "wifi-sec.psk", self.AP_PASS]).wait()

        if self.launch_hotstop():
            return {"status": True,
                    "message": "AP started",
                    "ssid": self.AP_SSID,
                    "password": self.AP_PASS,
                    "qrcode": self.generate_qr_code()}
        else:
            return {"status": False,
                    "message": "Error while creating AP."}

    def generate_qr_code(self) -> str:
        """Returns a QRCode based on the SSID and the password.

        Returns:
            str: String representing the QRcode as data scheme.
        """
        qrc = qrcode.make("WIFI:S:{};T:WPA;P:{};;".format(self.AP_SSID, self.AP_PASS))
        buffered = BytesIO()
        qrc.save(buffered, format="PNG")
        return "data:image/png;base64,{}".format(base64.b64encode(buffered.getvalue()).decode("utf8"))

    def launch_hotstop(self) -> bool:
        """This method enables the hotspot by asking nmcli to activate it, 
        then the result is checked against a regex in order to know if everything is good.

        Returns:
            bool: true if hotspot created.
        """
        sh = sp.Popen(["nmcli", "con", "up", self.AP_SSID], stdout=sp.PIPE, stderr=sp.PIPE)
        sh = sh.communicate()
        return re.match(".*/ActiveConnection/[0-9]+.*", sh[0].decode("utf8"))

    def check_internet(self) -> bool:
        """Check the internet link just with a small http request
        to an URL present in the configuration

        Returns:
            bool: True if everything works.
        """
        try:
            url = read_config(("network", "internet_check"))
            requests.get(url, timeout=10)
            return True
        except:
            return False

    def delete_hotspot(self) -> bool:
        """
            Delete the previously created hotspot. 
        """
        sh = sp.Popen(["nmcli", "con", "show"], stdout=sp.PIPE, stderr=sp.PIPE)
        for line in sh.communicate()[0].splitlines():
            line = line.decode('utf8')
            if self.iface_in in line:
                ssids = re.search("^[a-zA-Z]+\-[0-9a-f]{4}", line)
                if ssids:
                    sp.Popen(["nmcli", "con", "delete", ])
                    sh = sp.Popen(["nmcli", "con", "delete", ssids[0]], stdout=sp.PIPE, stderr=sp.PIPE)
                    sh = sh.communicate()

                    if re.match(".*[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}.*", sh[0].decode("utf8")):
                        return True
                    else:
                        return False
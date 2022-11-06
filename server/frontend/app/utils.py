#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import re
import shutil
import hashlib
import sqlite3
import subprocess as sp
from functools import reduce

import psutil
import yaml


def get_device_uuid() -> str:
    """Get the device UUID

    Returns:
        str: device uuid
    """
    uuid_not_found = False
    try:
        with open("/sys/class/dmi/id/product_uuid", "r") as uuid:
            return uuid.read()
    except:
        uuid_not_found = True

    try:
        with open("/proc/cpuinfo") as f:
            for line in f.readlines():
                if line.startswith("Serial"):
                    serial = line.split(":")[1].strip().encode('utf8')
                    hash = hashlib.md5(serial).hexdigest()
                    return f"{hash[0:8]}-{hash[8:12]}-{hash[12:16]}-{hash[16:20]}-{hash[20:]}"
    except:
        uuid_not_found = True
    
    if uuid_not_found:
        return "00000000-0000-0000-0000-000000000000"

def read_config(path) -> any:
    """Read a value from the configuration file

    Args:
        path (turple): The path as ('category', 'key')

    Returns:
        any: The configuration element.
    """
    config = yaml.load(open("/usr/share/spyguard/config.yaml", "r"), Loader=yaml.SafeLoader)
    return reduce(dict.get, path, config)

def write_config(cat, key, value):
    """Write a new value in the configuration file. 

    Args:
        cat (str): Category where to write
        key (str): Key to be written
        value (str): Value to write

    Returns:
        bool: True if successful.
    """
    try:
        config = yaml.load(open("/usr/share/spyguard/config.yaml", "r"), Loader=yaml.SafeLoader)
        config[cat][key] = value
        with open("/usr/share/spyguard/config.yaml", "w") as yaml_file:
            yaml_file.write(yaml.dump(config, default_flow_style=False))
            return True
    except:
        return False

def delete_captures() -> bool:
    """Delete potential capture zombies.

    Returns:
        bool: True if successful.
    """
    try:
        # Deleting zombies capture directories
        for d in os.listdir("/tmp/"):
            if re.match("[A-F0-9]{8}", d):
                shutil.rmtree(os.path.join("/tmp/", d))

        # Deleting zombies hotspot
        sh = sp.Popen(["nmcli", "con", "show"], stdout=sp.PIPE, stderr=sp.PIPE)
        for line in sh.communicate()[0].splitlines():
            res = re.search("^[a-zA-Z]+\-[0-9a-f]{4}", line.decode('utf8'))
            if res: sp.Popen(["nmcli", "con", "delete", res[0]])

        return True
    except:
        return False

def get_battery_level() -> int:
    """Get the battery level. 
       Returns 101 is the power supply is connected or not found.

    Returns:
        int: level of the battery.
    """
    if os.path.isdir("/sys/class/power_supply/"):
        for file_path in glob.glob("/sys/class/power_supply/*/*"):
            if file_path.endswith("/online"):
                with open(file_path, "r") as f:
                    if int(f.read()):
                        return 101
        for file_path in glob.glob("/sys/class/power_supply/*/*"):
            if file_path.endswith("/capacity"):
                with open(file_path, "r") as f:
                    return int(f.read())
    
    # If nothing found, return 101 as a default.
    return 101

def get_wifi_level() -> int:
    """Get the level of the WiFi interface (out)

    Returns:
        int: WiFi level
    """
    try:
        sh = sp.Popen(["iwconfig", read_config(('network', 'out'))], stdout=sp.PIPE, stderr=sp.PIPE)
        res = sh.communicate()[0].decode('utf8')
        m = re.search("Link Quality=(?P<quality>\d+)/(?P<quality_max>\d+)", res)
        return (int(m.group('quality'))/int(m.group('quality_max')))*100
    except:
        return 0

def get_iocs_number() -> int: 
    """Get number of IOCs in the database

    Returns:
        int: number of IOCs
    """
    with sqlite3.connect("/usr/share/spyguard/database.sqlite3") as c:
        cur = c.cursor()
        return len(cur.execute("SELECT * FROM iocs").fetchall())

def get_iocs(ioc_type) -> list:
    """Get a list of IOCs specified by their type.
    Returns:
        list: list containing the IOCs
    """
    with sqlite3.connect("/usr/share/spyguard/database.sqlite3") as c:
        cur = c.cursor()
        cur.execute("SELECT value, tag FROM iocs WHERE type = ? ORDER BY value", (ioc_type,))
        res = cur.fetchall()
        return [[r[0], r[1]] for r in res] if res is not None else []

def stop_monitoring() -> bool:
    """Just stop monitoring processes.

    Returns:
        bool: True by default.
    """
    for proc in psutil.process_iter():
        if proc.name() == "dumpcap":
            proc.terminate()

    sp.Popen(["suricatasc", "-c", "shutdown"])

    return True # Yeah, I know...
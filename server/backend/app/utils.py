#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import yaml
import os
from functools import reduce


def read_config(path):
    """
        Read a value from the configuration
        :return: value (it can be any type)
    """
    config = yaml.load(open("/usr/share/spyguard/config.yaml", "r"), Loader=yaml.SafeLoader)
    return reduce(dict.get, path, config)


def write_config(cat, key, value):
    """
        Write a new value in the configuration
        :return: bool, operation status
    """
    try:
        config = yaml.load(open("/usr/share/spyguard/config.yaml", "r"), Loader=yaml.SafeLoader)
        config[cat][key] = value
        with open(os.path.join(dir, "config.yaml"), "w") as yaml_file:
            yaml_file.write(yaml.dump(config, default_flow_style=False))
            return True
    except:
        return False


def get_watchers(watcher_type):
    """
        Read a value from the configuration
        :return: value (it can be any type)
    """
    watchers = yaml.load(open("/usr/share/spyguard/watchers.yaml", "r"), Loader=yaml.SafeLoader)
    for watcher in watchers["watchers"]:
        if watcher_type == watcher["type"]:
            yield watcher


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

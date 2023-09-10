#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
import subprocess as sp
import sys
import time
from datetime import datetime
from ipaddress import IPv4Address, IPv6Address

import ssl
import socket
import OpenSSL
import requests

import pydig
import whois
from publicsuffix2 import get_sld
from netaddr import IPAddress, IPNetwork
from classes.jarm import get_jarm
from utils import get_config, get_iocs, get_whitelist


class Engine():

    def __init__(self, capture_directory):

        # Set some vars.
        self.analysis_start = datetime.now()
        self.connected = self.check_internet()
        self.working_dir = capture_directory
        self.assets_dir = f"{capture_directory}/assets/"
        self.rules_file = "/tmp/rules.rules"
        self.pcap_path = os.path.join(self.working_dir, "capture.pcap")
        self.records = []
        self.alerts = []
        self.dns = []
        self.files = []
        self.whitelist = []
        self.uncategorized = []
        self.analysed = []
        self.dns_failed = []
        self.dns_checked = []
        self.cert_checked = []
        self.errors = []
        self.analysis_end = None

        # Get configuration
        self.heuristics_analysis = get_config(("analysis", "heuristics"))
        self.iocs_analysis = get_config(("analysis", "iocs"))
        self.whitelist_analysis = get_config(("analysis", "whitelist"))
        self.active_analysis = get_config(("analysis", "active"))
        self.userlang = get_config(("frontend", "user_lang"))
        self.max_ports = get_config(("analysis", "max_ports"))
        self.http_default_ports = get_config(("analysis", "http_default_ports"))
        self.tls_default_ports = get_config(("analysis", "tls_default_ports"))
        self.free_issuers = get_config(("analysis", "free_issuers"))
        self.max_alerts = get_config(("analysis", "max_alerts"))
        self.indicators_types = get_config(("analysis", "indicators_types"))
        
        # Save detection methods used.
        self.detection_methods = { "iocs" : self.iocs_analysis, 
                                   "heuristics" : self.heuristics_analysis, 
                                   "active" : self.active_analysis }

        # Retreive IOCs.
        if self.iocs_analysis:
            self.bl_cidrs = [[IPNetwork(cidr[0]), cidr[1]] for cidr in get_iocs("cidr")]
            self.bl_hosts = get_iocs("ip4addr") + get_iocs("ip6addr")
            self.tor_nodes = self.get_tor_nodes()
            self.bl_domains = get_iocs("domain")
            self.bl_freedns = get_iocs("freedns")
            self.bl_certs = get_iocs("sha1cert")
            self.bl_jarms = get_iocs("jarm")
            self.bl_nameservers = get_iocs("ns")
            self.bl_tlds = get_iocs("tld")

        # Retreive whitelisted items.
        if self.whitelist_analysis:
            self.wl_cidrs = [IPNetwork(cidr) for cidr in get_whitelist("cidr")]
            self.wl_hosts = get_whitelist("ip4addr") + get_whitelist("ip6addr") + self.get_public_ip()
            self.wl_domains = get_whitelist("domain")

        # Load template language
        if not re.match("^[a-z]{2,3}$", self.userlang): self.userlang = "en"
       
        with open(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "locales/{}.json".format(self.userlang))) as f:
            self.template = json.load(f)["alerts"]

    def check_internet(self) -> bool:
        """Check the internet link just with a small http request
        to an URL present in the configuration. If the link is down,
        retry 3 times.

        Returns:
            bool: True if everything works.
        """
        attempts = 3

        while True:
            try:
                url = get_config(("network", "internet_check"))
                requests.get(url, timeout=3)
                return True
            except:
                if attempts == 0:
                    return False
                else:
                    time.sleep(5)
                    attempts -= 1

    def get_public_ip(self) -> list:
        """Get the public IP address

        Returns:
            list: list containing the public IP address.
        """
        if self.connected:
            try:
                return [requests.get("https://api.ipify.org", timeout=3).text]
            except:
                return []
        else:
            return []

    def start_engine(self):
        """ This method starts suricata and then launch the 
            parsers to analyse the output logs. 
        """

        # Parse the eve.json file.
        self.parse_eve_file()

        # For each type of records, check it against heuristics.
        for record in self.records: 
            if self.whitelist_analysis: self.check_whitelist(record)
            self.check_domains(record)
            self.check_flow(record)
            self.check_tls(record)
            self.check_http(record)

        # Check for failed DNS answers (if spyguard not connected)
        for dnsname in list(set(self.dns_failed)):
            self.check_dnsname(dnsname)
        
    def parse_eve_file(self):
        """This method parses the eve.json file produced by suricata.
           For each record, it look at the record type and then append the self.record
           dictionnary which contains valuable data to look at suspicious stuff.
        """
        for record in open(f"{self.assets_dir}eve.json", "r").readlines():
            record = json.loads(record)
            try:
                if "flow" in record:
                    if "app_proto" not in record: record["app_proto"] = "failed"
                    proto = { "name" : record["app_proto"].upper() if record["app_proto"] != "failed" else record["proto"].upper(), "port" : record["dest_port"] if "dest_port" in record else -1 }
                   
                    if record["dest_ip"] not in [r["ip_dst"] for r in self.records]:
                        self.records.append({
                            "ip_dst" : record["dest_ip"],
                            "whitelisted" : False,
                            "suspicious" : False,
                            "protocols" : [proto],
                            "domains" : [],
                            "certificates" : []
                        })
                    else:
                        for rec in self.records:
                            if record["dest_ip"] == rec["ip_dst"]:
                                if proto not in rec["protocols"]:
                                    rec["protocols"].append(proto)
            except Exception as e:
                self.errors.append(f"Issue when processing the following eve record (flow): {json.dumps(record)}")

        for record in open(f"{self.assets_dir}eve.json", "r").readlines():
            record = json.loads(record)
            try:
                if "tls" in record:
                    for rec in self.records:
                        if record["dest_ip"] == rec["ip_dst"]:
                            if "version" in record["tls"]: 
                                if float(record["tls"]["version"].split(" ")[1]) < 1.3 and not "session_resumed" in record["tls"]:
                                    if record["tls"] not in rec["certificates"]:
                                        record["tls"]["port"] = record["dest_port"]
                                        rec["certificates"].append(record["tls"])
                                else:
                                    if "sni" in record["tls"] and record["tls"]["sni"] not in [c["sni"] for c in rec["certificates"]]:
                                        rec["certificates"].append({ "sni" : record["tls"]["sni"], "version" : record["tls"]["version"], "port" : record["dest_port"] })
                                    else:
                                        rec["certificates"].append({ "version" : record["tls"]["version"], "port" : record["dest_port"] })
            except Exception as e:
                self.errors.append(f"Issue when processing the following eve record (tls): {json.dumps(record)}")        

        for record in open(f"{self.assets_dir}eve.json", "r").readlines():
            record = json.loads(record)
            try:
                if "http" in record:
                    for rec in self.records:
                        if record["dest_ip"] == rec["ip_dst"]:
                            d = { "hostname" : record["http"]["hostname"] }
                            if "http_user_agent" in record["http"]:
                                d["user-agent"] = record["http"]["http_user_agent"]
                            if "http" in rec:
                                if not d in rec["http"]:
                                    rec["http"].append(d)
                            else:
                                rec["http"] = [d]
            except Exception as e:
                self.errors.append(f"Issue when processing the following eve record (http): {json.dumps(record)}")        

        for record in open(f"{self.assets_dir}eve.json", "r").readlines():
            record = json.loads(record)
            try:
                if "dns" in record:
                    if record["dns"]["type"] == "answer":
                        for rec in self.records:
                            if record["dns"]["rcode"] == "NOERROR":
                                if "grouped" in record["dns"]:
                                    if "A" in record["dns"]["grouped"] and rec["ip_dst"] in record["dns"]["grouped"]["A"]:
                                        if record["dns"]["rrname"] not in rec["domains"]:
                                            rec["domains"].append(record["dns"]["rrname"])
                                    elif "AAAA" in record["dns"]["grouped"] and rec["ip_dst"] in record["dns"]["grouped"]["AAAA"]:
                                        if record["dns"]["rrname"] not in rec["domains"]:
                                            rec["domains"].append(record["dns"]["rrname"])
                            elif record["dns"]["rcode"] == "SERVFAIL":
                                self.dns_failed.append(record["dns"]["rrname"])
            except Exception as e:
                self.errors.append(f"Issue when processing the following eve record (dns answer): {json.dumps(record)}")

        # This pass is if SpyGuard is not connected to Internet.
        # We still analyze the un answered DNS queries.
        for record in open(f"{self.assets_dir}eve.json", "r").readlines():
            record = json.loads(record)
            try:
                if "dns" in record:
                    if record["dns"]["type"] == "query":
                        if record["dns"]["rrname"] not in sum([r["domains"] for r in self.records], []):
                             self.records.append({
                                "ip_dst" : "--",
                                "whitelisted" : False,
                                "suspicious" : False,
                                "protocols" : [{"name" : "DNS", "port" : "53"}],
                                "domains" : [record["dns"]["rrname"]],
                                "certificates" : []
                            })
            except Exception as e:
                self.errors.append(f"Issue when processing the following eve record (dns query): {json.dumps(record)}")        

        for record in open(f"{self.assets_dir}eve.json", "r").readlines():
            record = json.loads(record)
            try:
                if "alert" in record and record["event_type"] == "alert":
                    for rec in self.records:
                        if record["dest_ip"] == rec["ip_dst"]:
                            rec["suspicious"] = True
                            self.alerts.append({"title": self.template["SNORT-01"]["title"].format(record["alert"]["signature"]),
                                                "description": self.template["SNORT-01"]["description"].format(rec["ip_dst"]),
                                                "host": rec["ip_dst"],
                                                "level": "High",
                                                "id": "SNORT-01"})

            except Exception as e:
                self.errors.append(f"Issue when processing the following eve record (dns answer): {json.dumps(record)}")


    def check_whitelist(self, record):
        """ This method is asked on each record. It:

            1. Check if the associated IP(v4/6) Address can be whitelisted 
            2. Check if one of the associated domain names can be whitelisted. 

            If its the case, the "whitelisted" key of the record is set to True. 
            Therefore, the record will be ignored for the rest of the analysis.  
        Args:
            record (dict): record to be processed. 
        """

        try: 
            assert IPv4Address(record["ip_dst"])

            if IPv4Address('224.0.0.0') <= IPv4Address(record["ip_dst"]) <= IPv4Address('239.255.255.255'):
                record["whitelisted"] = True
                return 

            for cidr in self.wl_cidrs:
                if IPAddress(record["ip_dst"]) in cidr:
                    record["whitelisted"] = True
                    return 

            for ip in self.wl_hosts:
                if record["ip_dst"] == ip:
                    record["whitelisted"] = True
                    return 
        except:
            pass
        
        try:
            assert IPv6Address(record["ip_dst"])

            if [record["ip_dst"].startswith(prefix) for prefix in ["fe80", "fc00", "ff02"]]: 
                record["whitelisted"] = True
                return

            for ip in self.wl_hosts:
                if record["ip_dst"] == ip:
                    record["whitelisted"] = True
                    return
        except:
            pass
        
        # We check if at least one of the associated 
        # domains is whitelisted
        for dom in self.wl_domains:
            for domain in record["domains"]:
                if domain.endswith(dom):
                    record["whitelisted"] = True
                    return
        
    def check_domains(self, record):
        """Check the domains associated to each record.
           First this method checks if the record is whitelisted. If not:
              1. Leverage a low alert if the record don't have any associated DNSName
              2. Check each domain associated to the record by calling check_dnsname.
        Args:
            record (dict): record to be processed.
        """
        if record["whitelisted"]: return 

        if self.heuristics_analysis:
            # Otherwise, we alert the user that an IP haven't been resolved by 
            # a DNS answer during the session...
            if record["domains"] == []:
                record["suspicious"] = True
                self.alerts.append({"title": self.template["PROTO-05"]["title"].format(record["ip_dst"]),
                                    "description": self.template["PROTO-05"]["description"].format(record["ip_dst"]),
                                    "host": record["ip_dst"],
                                    "level": "Low",
                                    "id": "PROTO-05"})

        # Check each associated domain.
        for domain in record["domains"]:
            if self.check_dnsname(domain): 
                record["suspicious"] = True

    def check_dnsname(self, dnsname):
        """Check a domain name against a set of IOCs / heuristics.
              1. Check if the parent domain is blacklisted. 
              2. Check if the parent domain is a Free DNS.
              3. Check if the domain extension is a suspicious TLD.
              4. Check if the name servers associated to the domain are suspicious.
              5. Check if the domain have been registered recently - less than one year.
        Args:
            record (dict): record to be processed.
        Returns:
            supicious (bool) : if an alert has been leveraged. 
        """
        suspicious = False
        
        if self.iocs_analysis:
            for domain in self.bl_domains:
                if dnsname.endswith(domain[0]) and any(t in self.indicators_types for t in [domain[1], "all"]):
                    if domain[1] == "dual": 
                        suspicious = True
                        self.alerts.append({"title": self.template["IOC-12"]["title"],
                                            "description": self.template["IOC-12"]["description"].format(domain[0]),
                                            "host": domain[0],
                                            "level": "Low",
                                            "id": "IOC-12"})
                    elif domain[1] == "tracker": 
                        suspicious = True
                        self.alerts.append({"title": self.template["IOC-04"]["title"].format(domain[0], "tracker"),
                                            "description": self.template["IOC-04"]["description"].format(domain[0], "tracker"),
                                            "host": domain[0],
                                            "level": "Low",
                                            "id": "IOC-04"})
                    elif domain[1] == "doh": 
                        suspicious = True
                        self.alerts.append({"title": self.template["IOC-13"]["title"].format(f"{dnsname}"),
                                                "description": self.template["IOC-13"]["description"].format(f"{dnsname}"),
                                                "host": dnsname,
                                                "level": "Low",
                                                "id": "IOC-13"})
                    else:
                        suspicious = True
                        self.alerts.append({"title": self.template["IOC-03"]["title"].format(dnsname, domain[1].upper()),
                                            "description": self.template["IOC-03"]["description"].format(dnsname),
                                            "host": dnsname,
                                            "level": "High",
                                            "id": "IOC-03"})
            for domain in self.bl_freedns:
                if dnsname.endswith(domain[0]) and any(t in self.indicators_types for t in [domain[1], "all"]):
                    suspicious = True
                    self.alerts.append({"title": self.template["IOC-05"]["title"].format(dnsname),
                                        "description": self.template["IOC-05"]["description"].format(dnsname),
                                        "host": dnsname,
                                        "level": "Moderate",
                                        "id": "IOC-05"})
                    
        if self.heuristics_analysis:        
            for domain in self.bl_tlds:
                if dnsname.endswith(domain[0]) and any(t in self.indicators_types for t in [domain[1], "all"]):
                    suspicious = True
                    self.alerts.append({"title": self.template["IOC-06"]["title"].format(dnsname),
                                        "description": self.template["IOC-06"]["description"].format(dnsname, domain[0]),
                                        "host": dnsname,
                                        "level": "Low",
                                        "id": "IOC-06"})
                    
        if self.active_analysis and self.connected:
            domain = get_sld(dnsname)
            if domain not in self.dns_checked:
                self.dns_checked.append(domain)
                try:
                    name_servers = pydig.query(domain, "NS")
                    if len(name_servers):
                        for ns in self.bl_nameservers:
                            if name_servers[0].endswith(".{}.".format(ns[0])) and any(t in self.indicators_types for t in [ns[1], "all"]):
                                suspicious = True
                                self.alerts.append({"title": self.template["ACT-01"]["title"].format(dnsname, name_servers[0]),
                                                    "description": self.template["ACT-01"]["description"].format(dnsname),
                                                    "host": dnsname,
                                                    "level": "Moderate",
                                                    "id": "ACT-01"})
                except Exception as e:
                    self.errors.append(f"Issue when doing a dig NS query to {domain}, are you connected? Error: {str(e)}")        

                try:
                    whois_record = whois.whois(domain)
                    creation_date = whois_record.creation_date if type(whois_record.creation_date) is not list else whois_record.creation_date[0]
                    creation_days = abs((datetime.now() - creation_date).days)
                    if creation_days < 365:
                        suspicious = True
                        self.alerts.append({"title": self.template["ACT-02"]["title"].format(dnsname, creation_days),
                                            "description": self.template["ACT-02"]["description"].format(dnsname),
                                            "host": dnsname,
                                            "level": "Moderate",
                                            "id": "ACT-02"})
                except Exception as e:
                    self.errors.append(f"Issue when doing a WHOIS query to {domain}, are you connected? Error: {str(e)}")
        
        return suspicious
        

    def check_flow(self, record):
        """Check a network flow against a set of IOCs / heuristics.
              1. Check if the IP Address is blacklisted 
              2. Check if the IP Address is inside a blacklisted CIDR
              3. Check if the UDP or ICMP protocol is going outside of the local network. 
              4. Check if the HTTP protocol is not using default HTTP ports.
              5. Check if the network flow is using a port > 1024.
        Args:
            record (dict): record to be processed.
        Returns:
            supicious (bool) : if an alert has been leveraged. 
        """
        if record["whitelisted"]: return 

        resolved_host = record["domains"][0] if len(record["domains"]) else record["ip_dst"]

        if self.iocs_analysis:
            for host in self.bl_hosts:
                if record["ip_dst"] == host[0] and any(t in self.indicators_types for t in [host[1], "all"]):
                    if host[1] == "dual": 
                        record["suspicious"] = True
                        self.alerts.append({"title": self.template["IOC-12"]["title"],
                                            "description": self.template["IOC-12"]["description"].format(resolved_host),
                                            "host": resolved_host,
                                            "level": "Low",
                                            "id": "IOC-12"})
                    if host[1] == "tracker": 
                        record["suspicious"] = True
                        self.alerts.append({"title": self.template["IOC-04"]["title"].format(resolved_host, "tracker"),
                                            "description": self.template["IOC-04"]["description"].format(resolved_host, "tracker"),
                                            "host": resolved_host,
                                            "level": "Low",
                                            "id": "IOC-04"})
                    elif host[1] == "doh":
                        if 443 in [p["port"] for p in record["protocols"]]:
                            record["suspicious"] = True
                            self.alerts.append({"title": self.template["IOC-13"]["title"].format(f"{resolved_host}"),
                                                "description": self.template["IOC-13"]["description"].format(f"{resolved_host}"),
                                                "host": resolved_host,
                                                "level": "Low",
                                                "id": "IOC-13"})
                    else:
                        record["suspicious"] = True
                        self.alerts.append({"title": self.template["IOC-01"]["title"].format(resolved_host, record["ip_dst"], host[1].upper()),
                                            "description": self.template["IOC-01"]["description"].format(f"{resolved_host} ({record['ip_dst']})"),
                                            "host": resolved_host,
                                            "level": "High",
                                            "id": "IOC-01"})
                    break
            
            for host in self.tor_nodes:
                if record["ip_dst"] == host:
                    record["suspicious"] = True
                    self.alerts.append({"title": self.template["IOC-11"]["title"].format(resolved_host, record["ip_dst"]),
                                        "description": self.template["IOC-11"]["description"].format(f"{resolved_host} ({record['ip_dst']})"),
                                        "host": resolved_host,
                                        "level": "High",
                                        "id": "IOC-11"})
                    break

            for cidr in self.bl_cidrs:
                try:
                    if IPAddress(record["ip_dst"]) in cidr[0] and any(t in self.indicators_types for t in [cidr[1], "all"]):
                        record["suspicious"] = True
                        self.alerts.append({"title": self.template["IOC-02"]["title"].format(resolved_host, cidr[0], cidr[1].upper()),
                                            "description": self.template["IOC-02"]["description"].format(record["ip_dst"]),
                                            "host": resolved_host,
                                            "level": "Moderate",
                                            "id": "IOC-02"})
                except:
                    continue

        if self.heuristics_analysis:
            for protocol in record["protocols"]:
                if protocol["name"] in ["UDP", "ICMP", "IPV6-ICMP"]:
                    record["suspicious"] = True
                    self.alerts.append({"title": self.template["PROTO-01"]["title"].format(protocol["name"], resolved_host),
                                        "description": self.template["PROTO-01"]["description"].format(protocol["name"], resolved_host),
                                        "host": resolved_host,
                                        "level": "Moderate",
                                        "id": "PROTO-01"})
                try:
                    if protocol["port"] >= int(self.max_ports):
                        record["suspicious"] = True
                        self.alerts.append({"title": self.template["PROTO-02"]["title"].format("", resolved_host,  self.max_ports),
                                            "description": self.template["PROTO-02"]["description"].format("", resolved_host, protocol["port"]),
                                            "host": resolved_host,
                                            "level": "Low",
                                            "id": "PROTO-02"})
                except:
                    pass
                
                if protocol["name"] == "HTTP":
                    record["suspicious"] = True
                    self.alerts.append({"title": self.template["PROTO-03"]["title"].format(resolved_host),
                                        "description": self.template["PROTO-03"]["description"].format(resolved_host),
                                        "host":  resolved_host,
                                        "level": "Low",
                                        "id": "PROTO-03"})

                if protocol["name"] == "HTTP" and protocol["port"] not in self.http_default_ports:
                    record["suspicious"] = True
                    self.alerts.append({"title": self.template["PROTO-04"]["title"].format(resolved_host, protocol["port"]),
                                        "description": self.template["PROTO-04"]["description"].format(resolved_host, protocol["port"]),
                                        "host":  resolved_host,
                                        "level": "Moderate",
                                        "id": "PROTO-04"})

    def check_tls(self, record):
        """Check a TLS protocol and certificates against a set of IOCs / heuristics.
        Note since TLS 1.3, the certificate is not exchanged in clear text, therefore 
        we need to check it "actively" via the method active_check_ssl. 

              1. Check if the TLS record is not using default TLS ports.
              2. Check if one of the certificates is a free one, like Let's Encrypt.
              3. Check if the certificate is auto-signed. 
              4. If the certificate has an SNI, check the domain by calling check_dnsname.
        Args:
            record (dict): record to be processed.
        Returns:
            supicious (bool) : if an alert has been leveraged. 
        """
        if record["whitelisted"]: return

        resolved_host = record["domains"][0] if len(record["domains"]) else record["ip_dst"]
                
        for certificate in record["certificates"]:

            try:
                if "sni" in certificate and certificate["sni"] not in record["domains"]:
                    if certificate["sni"]:
                        if self.check_dnsname(certificate["sni"]):
                            record["suspicious"] = True

                if certificate["port"] not in self.tls_default_ports:
                    record["suspicious"] = True
                    self.alerts.append({"title": self.template["SSL-01"]["title"].format(certificate["port"], resolved_host),
                                        "description": self.template["SSL-01"]["description"].format(resolved_host),
                                        "host": resolved_host,
                                        "level": "Moderate",
                                        "id": "SSL-01"})

                if float(certificate["version"].split(" ")[1]) < 1.3 and "issuerdn" in certificate:

                    if certificate["issuerdn"] in self.free_issuers:
                        record["suspicious"] = True
                        self.alerts.append({"title": self.template["SSL-02"]["title"].format(resolved_host),
                                            "description": self.template["SSL-02"]["description"],
                                            "host": resolved_host,
                                            "level": "Moderate",
                                            "id": "SSL-02"})

                    elif certificate["issuerdn"] == certificate["subject"]:
                        record["suspicious"] = True
                        self.alerts.append({"title": self.template["SSL-03"]["title"].format(resolved_host),
                                            "description": self.template["SSL-03"]["description"].format(resolved_host),
                                            "host": resolved_host,
                                            "level": "Moderate",
                                            "id": "SSL-03"})
                else:
                    if self.active_analysis and self.connected:
                        if "sni" in certificate:
                            if certificate["sni"] not in self.cert_checked:
                                self.cert_checked.append(certificate["sni"])
                                if self.active_check_ssl(certificate["sni"], certificate["port"]):
                                    record["suspicious"] = True
                                    break
                        else:
                            if resolved_host not in self.cert_checked:
                                self.cert_checked.append(resolved_host)
                                if self.active_check_ssl(resolved_host, certificate["port"]):
                                    record["suspicious"] = True
                                    break
            except Exception as e:
                self.errors.append(f"Issue when processing the following certificate (check_tls): {json.dumps(certificate)}")
    
    def get_tor_nodes(self) -> list:
        """Get a list of TOR nodes from dan.me.uk.

        Returns:
            list: list of TOR nodes
        """

        nodes = []
        if os.path.exists("/tmp/tor_nodes.lst"):
            with open("/tmp/tor_nodes.lst", "r") as f:
                for l in f.readlines():
                    nodes.append(l.strip())
        else:
            if self.connected:
                try:
                    nodes_list = requests.get("https://www.dan.me.uk/torlist/", timeout=10).text
                    with open("/tmp/tor_nodes.lst", "w+") as f:
                        f.write(nodes_list)
                    for l in nodes_list.splitlines():
                        nodes.append(l.strip())
                except:
                    self.errors.append(f"Issue when trying to get TOR nodes from dan.me.uk")
        return nodes


    def check_http(self, record):
        """Check the HTTP hostname against a set of IOCs / heuristics.
        Args:
            record (dict): record to be processed.
        Returns:
            supicious (bool) : if an alert has been leveraged. 
        """
        if record["whitelisted"]: return

        if "http" in record:
            for http in record["http"]:
                if http["hostname"] not in record["domains"]:
                    if re.match("^[a-z\.0-9\-]+\.[a-z\-]{2,}$", http["hostname"]):
                        if http["hostname"]:
                            if self.check_dnsname(http["hostname"]):
                                record["suspicious"] = True

    def active_check_ssl(self, host, port):
        """This method:
        
        1. Check the issuer and subject of a certificate directly by connecting
        to the remote server in order to bypass TLS 1.3+ restrictions. 
        Most of this method was been taken from: https://tinyurl.com/3vsvhu79

        2. Get the JARM of the remote server by using the standard poc library
        from sales force. 

        Args:
            host (str): Host to connect to
            port (int): Port to connect to
        """
        try:
            suspect = False
            context = ssl.create_default_context()
            conn = socket.create_connection((host, port))
            sock = context.wrap_socket(conn, server_hostname=host)
            sock.settimeout(5)
            try:
                der_cert = sock.getpeercert(True)
            finally:
                sock.close()

            if "der_cert" in locals():

                certificate = ssl.DER_cert_to_PEM_cert(der_cert)
                x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, certificate)

                issuer = dict(x509.get_issuer().get_components())
                subject = dict(x509.get_subject().get_components())
                certhash = x509.digest("sha1").decode("utf8").replace(":", "").lower()
                issuer = ", ".join(f"{k.decode('utf8')}={v.decode('utf8')}" for k, v in issuer.items())
                subject = ", ".join(f"{k.decode('utf8')}={v.decode('utf8')}" for k, v in subject.items())

                if issuer in self.free_issuers:
                    self.alerts.append({"title": self.template["SSL-02"]["title"].format(host),
                                        "description": self.template["SSL-02"]["description"],
                                        "host": host,
                                        "level": "Moderate",
                                        "id": "SSL-02"})
                    suspect = True

                if issuer == subject:
                    self.alerts.append({"title": self.template["SSL-03"]["title"].format(host),
                                        "description": self.template["SSL-03"]["description"].format(host),
                                        "host": host,
                                        "level": "Moderate",
                                        "id": "SSL-03"})
                    suspect = True
  
                if self.iocs_analysis:
                    for cert in self.bl_certs:
                        if cert[0] == certhash and any(t in self.indicators_types for t in [cert[1], "all"]):
                            self.alerts.append({"title": self.template["SSL-04"]["title"].format(host, cert[1].upper()),
                                                "description": self.template["SSL-04"]["description"].format(host),
                                                "host": host,
                                                "level": "High",
                                                "id": "SSL-04"})
                            suspect = True
                    
                    if self.bl_jarms:
                        host_jarm = get_jarm(host, port)
                        for jarm in self.bl_jarms:
                            if jarm[0] == host_jarm and any(t in self.indicators_types for t in [jarm[1], "all"]):
                                self.alerts.append({"title": self.template["SSL-05"]["title"].format(host, cert[1].upper()),
                                                    "description": self.template["SSL-05"]["description"].format(host),
                                                    "host": host,
                                                    "level": "High",
                                                    "id": "SSL-05"})
                                suspect = True
            return suspect
        except:
            self.errors.append(f"Issue when trying to grab the SSL certificate located at {host}:{port}")
            return False

    def get_alerts(self):
        """Retrieves the alerts triggered during the analysis

        Returns:
            list: list of the alerts.
        """
        self.analysis_end = datetime.now()
        return [dict(t) for t in {tuple(d.items()) for d in self.alerts}]

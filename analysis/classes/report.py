import weasyprint
import os
import json
import hashlib
import re
import sys

from weasyprint import HTML
from pathlib import Path
from datetime import datetime
from utils import get_config


class Report(object):

    def __init__(self, capture_directory, analysis_duration):
        self.capture_directory = capture_directory
        self.alerts = self.read_json(os.path.join(capture_directory, "assets/alerts.json"))
        self.records = self.read_json(os.path.join(capture_directory, "assets/records.json"))
        self.methods = self.read_json(os.path.join(capture_directory, "assets/detection_methods.json"))
        self.device = self.read_json(os.path.join(capture_directory, "assets/device.json"))
        self.capinfos = self.read_json(os.path.join(capture_directory, "assets/capinfos.json"))
        self.instance = self.read_json(os.path.join(capture_directory, "assets/instance.json"))
        self.analysis_duration = analysis_duration

        with open(os.path.join(self.capture_directory, "capture.pcap"), "rb") as f:
            self.capture_sha1 = hashlib.sha1(f.read()).hexdigest()

        self.userlang = get_config(("frontend", "user_lang"))

        # Load template language
        if not re.match("^[a-z]{2,3}$", self.userlang):
            self.userlang = "en"
        with open(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "locales/{}.json".format(self.userlang))) as f:
            self.template = json.load(f)["report"]

    def read_json(self, json_path):
        """Read a JSON 

        Args:
            json_path (_type_): _description_

        Returns:
            _type_: _description_
        """
        with open(json_path, "r") as json_file:
            return json.load(json_file)

    def generate_report(self):
        """Generate the full report and save it as report.pdf """

        content = self.generate_page_header()
        content += self.generate_header()
        content += self.generate_warning()
        content += self.generate_alerts()
        content += self.generate_suspect_conns_block()
        content += self.generate_uncat_conns_block()
        content += self.generate_whitelist_block()

        htmldoc = HTML(string=content, base_url="").write_pdf()
        Path(os.path.join(self.capture_directory,
                          "report.pdf")).write_bytes(htmldoc)

    def generate_warning(self):
        """Generate the main warning message on the report

        Returns:
            string: HTML code of the main warning message.
        """
        if len(self.alerts["high"]):
            msg = "<div class=\"warning high\">"
            msg += self.template["high_msg"].format(
                self.nb_translate(len(self.alerts["high"])))
            msg += "</div>"
            return msg
        elif len(self.alerts["moderate"]):
            msg = "<div class=\"warning moderate\">"
            msg += self.template["moderate_msg"].format(
                self.nb_translate(len(self.alerts["moderate"])))
            msg += "</div>"
            return msg
        elif len(self.alerts["low"]):
            msg = "<div class=\"warning low\">"
            msg += self.template["low_msg"].format(
                self.nb_translate(len(self.alerts["low"])))
            msg += "</div>"
            return msg
        else:
            msg = "<div class=\"warning low\">"
            msg += self.template["none_msg"]
            msg += "</div>"
            return msg

    def nb_translate(self, nb):
        """ Translate a number in a string.

        Args:
            nb (int): integer

        Returns:
            string: A translated string related to the integer
        """
        a = self.template["numbers"]
        return a[nb-1] if nb <= 9 else str(nb)

    def generate_suspect_conns_block(self):
        """Generate the block and the table of communications categorized as suspect.

        Returns:
            str: HTML block of the suspect communications
        """

        tbody = ""

        for record in self.records:
            if record["suspicious"] == True:
                tbody += "<tr>"
                tbody += f"<td>{', '.join([p['name'] for p in record['protocols']])}</td>"
                tbody += f"<td>{', '.join(record['domains'])}</td>"
                tbody += f"<td>{record['ip_dst']}</td>"
                tbody += f"<td>{', '.join([str(p['port']) if p['port'] != -1 else '--' for p in record['protocols']])}</td>"
                tbody += "</tr>"

        if len(tbody):
            title = f"<h2>{self.template['suspect_title']}</h2>"
            table = "<table>"
            table += "    <thead>"
            table += "        <tr>"
            table += f"             <th>{self.template['protocol']}</th>"
            table += f"             <th>{self.template['domain']}</th>"
            table += f"             <th>{self.template['dst_ip']}</th>"
            table += f"             <th>{self.template['dst_port']}</th>"
            table += "        </tr>"
            table += "    </thead>"
            table += "<tbody>"
            table += tbody
            table += "</tbody></table>"
            return title + table
        else:
            return ""

    def generate_uncat_conns_block(self):
        """Generate the block and the table of the uncategorized communications

        Returns:
            str: HTML block of the uncategorized communications
        """
        tbody = ""

        for record in self.records:
            if record["suspicious"] == False and record["whitelisted"] == False:
                tbody += "<tr>"
                tbody += f"<td>{', '.join([p['name'] for p in record['protocols']])}</td>"
                tbody += f"<td>{', '.join(record['domains'])}</td>"
                tbody += f"<td>{record['ip_dst']}</td>"
                tbody += f"<td>{', '.join([str(p['port']) if p['port'] != -1 else '--' for p in record['protocols']])}</td>"
                tbody += "</tr>"

        if len(tbody):
            title = "<h2>{}</h2>".format(self.template["uncat_title"])
            table = "<table>"
            table += "    <thead>"
            table += "        <tr>"
            table += f"             <th>{self.template['protocol']}</th>"
            table += f"             <th>{self.template['domain']}</th>"
            table += f"             <th>{self.template['dst_ip']}</th>"
            table += f"             <th>{self.template['dst_port']}</th>"
            table += "        </tr>"
            table += "    </thead>"
            table += "<tbody>"
            table += tbody
            table += "</tbody></table>"
            return title + table
        else:
            return ""

    def generate_whitelist_block(self):
        """Generate the block and the table of the whitelisted communications

        Returns:
            str: HTML block of the whitelisted communications
        """

        tbody = ""

        for record in self.records:
            if record["whitelisted"] == True:
                tbody += "<tr>"
                tbody += f"<td>{', '.join([p['name'] for p in record['protocols']])}</td>"
                tbody += f"<td>{', '.join(record['domains'])}</td>"
                tbody += f"<td>{record['ip_dst']}</td>"
                tbody += f"<td>{', '.join([str(p['port']) if p['port'] != -1 else '--' for p in record['protocols']])}</td>"
                tbody += "</tr>"

        if len(tbody):
            title = "<h2>{}</h2>".format(self.template["whitelist_title"])
            table = "<table>"
            table += "    <thead>"
            table += "        <tr>"
            table += f"             <th>{self.template['protocol']}</th>"
            table += f"             <th>{self.template['domain']}</th>"
            table += f"             <th>{self.template['dst_ip']}</th>"
            table += f"             <th>{self.template['dst_port']}</th>"
            table += "        </tr>"
            table += "    </thead>"
            table += "<tbody>"
            table += tbody
            table += "</tbody></table>"
            return title + table
        else:
            return ""

    def generate_header(self):
        """Generate the report headers with the capture's metadata.

        Returns:
            str: HTML block containing the data.
        """
        header = "<div class=\"header\">"
        header += "<div class=\"logo\"></div>"
        header += f"<p><br /><strong>{self.template['device_mac']}: {self.device['mac_address']}</strong><br />"
        header += f"{self.template['detection_methods']}: {'☑' if self.methods['iocs'] else '☐'} IOCs {'☑' if self.methods['heuristics'] else '☐'}  Heuristics {'☑' if self.methods['active'] else '☐'} Active analysis <br />"
        header += f"{self.template['capture_sha1']}: {self.capture_sha1}<br />"
        header += f"{self.template['instance_uuid']}: {self.instance['instance_uuid']}<br />"
        header += f"{self.template['report_generated_on']} {datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}<br />"
        if self.capinfos is not None:
            header += f"{self.template['capture_duration']}: {self.capinfos['Capture duration'].split(' ')[0]} {self.template['seconds']}<br />"
            header += f"{self.template['analysis_duration']}: {self.analysis_duration} {self.template['seconds']}<br />"
            header += f"{self.template['packets_number']}: {self.capinfos['Number of packets']}<br />"
        header += "</p>"
        header += "</div>"
        return header

    def generate_alerts(self):
        """Generate a block embedding the alerts triggered during the analysis.

        Returns:
            str: HTML block containing the data.
        """
        alerts = "<ul class=\"alerts\">"
        for alert in self.alerts["high"]:
            alerts += "<li class =\"alert\">"
            alerts += "<span class=\"high-label\">High</span>"
            alerts += "<span class=\"alert-id\">{}</span>".format(alert["id"])
            alerts += "<div class = \"alert-body\">"
            alerts += "<span class=\"title\">{}</span>".format(alert["title"])
            alerts += "<p class=\"description\">{}</p>".format(
                alert["description"])
            alerts += "</div>"
            alerts += "</li>"

        for alert in self.alerts["moderate"]:
            alerts += "<li class =\"alert\">"
            alerts += "<span class=\"moderate-label\">moderate</span>"
            alerts += "<span class=\"alert-id\">{}</span>".format(alert["id"])
            alerts += "<div class = \"alert-body\">"
            alerts += "<span class=\"title\">{}</span>".format(alert["title"])
            alerts += "<p class=\"description\">{}</p>".format(
                alert["description"])
            alerts += "</div>"
            alerts += "</li>"
        for alert in self.alerts["low"]:
            alerts += "<li class =\"alert\">"
            alerts += "<span class=\"low-label\">low</span>"
            alerts += "<span class=\"alert-id\">{}</span>".format(alert["id"])
            alerts += "<div class = \"alert-body\">"
            alerts += "<span class=\"title\">{}</span>".format(alert["title"])
            alerts += "<p class=\"description\">{}</p>".format(
                alert["description"])
            alerts += "</div>"
            alerts += "</li>"

        alerts += "</ul>"
        return alerts

    def generate_page_footer(self):
        """Generate the page footer

        Returns:
            str: HTML block closing the page
        """
        return "</body></html>"

    def generate_page_header(self):
        """Generate the page header

        Returns:
            str: HTML block containing the page header with the CSS.
        """
        return """<html
                    <head>
                        <style>
                            * {
                                font-family: Arial, Helvetica, sans-serif;
                            }

                            h2 {
                                padding-top: 30px;
                                font-weight: 400;
                                font-size: 18px;
                            }

                            td {
                                width: auto;
                                padding: 10px;
                            }

                            table {
                                background: #FFF;
                                border: 2px solid #FAFAFA;
                                border-radius: 5px;
                                border-collapse: separate;
                                border-spacing: 0px;
                                width: 100%;
                                font-size: 12px;
                            }

                            p {
                                font-size: 13px;
                            }

                            thead tr th {
                                border-bottom: 1px solid #CCC;
                                border-collapse: separate;
                                border-spacing: 5px 5px;
                                background-color: #FFF;
                                padding: 10px;
                                text-align: left;
                            }

                            tbody tr#first td {
                                border-top: 3px solid #4d4d4d;
                                border-collapse: separate;
                                border-spacing: 5px 5px;
                            }

                            tr:nth-of-type(odd) {
                                background-color: #fafafa;
                            }

                            .logo {
                                background-image: url("data:image/svg+xml;base64;base64,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");
                                width: 230px;
                                height: 60px;
                                background-size: cover;
                                position: absolute;
                                right: 0px;
                            }

                            .warning {
                                padding: 10px;
                                text-align: center;
                                border-radius: 5px;
                                color: #FFF;
                                margin-top: 40px;
                                margin-bottom: 40px;
                                font-weight:900;
                            }

                            .high {
                                background-color: #F44336;
                            }

                            .moderate {
                                background-color: #ff7e33;
                            }

                            .low {
                                background-color: #4fce0e;
                            }

                            ul {
                                list-style: none;
                                margin: 0;
                                padding: 0;
                            }

                            .alert {
                                margin-top: 15px;
                            }

                            .alert-body {
                                background-color: #FFF;
                                list-style: none;
                                padding: 10px;
                                border-radius: 5px;
                                border: 1px solid #EEE;
                                margin-top: 3px;
                            }

                            .alert-body>.title {
                                display: block;
                                padding: 5px 5px 5px 10px;
                                font-size: 13px;
                            }

                            .high-label {
                                background-color: #F44336;
                                padding: 5px;
                                text-transform: uppercase;
                                font-size: 10px;
                                font-weight: bold;
                                border-radius: 3px 0px 0px 0px;
                                margin: 0px;
                                color: #FFF;
                                margin-left: 10px;
                            }

                            .moderate-label {
                                background-color: #ff7e33;
                                padding: 5px;
                                text-transform: uppercase;
                                font-size: 10px;
                                font-weight: bold;
                                border-radius: 3px 0px 0px 0px;
                                margin: 0px;
                                color: #FFF;
                                margin-left: 10px;
                            }

                            .low-label {
                                background-color: #4fce0e;
                                padding: 5px;
                                text-transform: uppercase;
                                font-size: 10px;
                                font-weight: bold;
                                border-radius: 3px 0px 0px 0px;
                                margin: 0px;
                                color: #FFF;
                                margin-left: 10px;
                            }

                            .description {
                                margin: 0;
                                padding: 10px;
                                color:#333;
                                font-size:12px;
                            }

                            ul {
                                list-style: none;
                                margin: 0;
                                padding: 0;
                            }

                            .alert-id {
                                background-color: #636363;
                                padding: 5px;
                                text-transform: uppercase;
                                font-size: 10px;
                                font-weight: bold;
                                border-radius: 0px 3px 0px 0px;
                                margin: 0px;
                                color: #FFF;
                                margin-right: 10px;
                            }
                 
                            .header>p {
                                font-size:12px;
                            }
                            @page {
                                @top-center { 
                                    content: "REPORT_HEADER - Page " counter(page) " / " counter(pages) ".";
                                    font-size:12px;
                                    color:#CCC;
                                }
                                @bottom-center { 
                                    content: "REPORT_FOOTER";
                                    font-size:12px;  
                                    color:#CCC;
                                }
                            }   
                        </style>
                    </head>
                    <body>""".replace("REPORT_HEADER", "{} {}".format(self.template["report_for_the_capture"], self.capture_sha1)).replace("REPORT_FOOTER", self.template["report_footer"])

#!/usr/bin/python3
"""
    Copyright (c) 2024 Penterep Security s.r.o.

    ptmethods - HTTP Methods Testing Tool

    ptmethods is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ptmethods is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ptmethods.  If not, see <https://www.gnu.org/licenses/>.
"""


import argparse
import re
import sys; sys.path.append(__file__.rsplit("/", 1)[0])
import urllib

import requests

from _version import __version__
from ptlibs import ptjsonlib, ptmisclib, ptnethelper, ptprinthelper
from ptlibs.http import http_client

from modules.helpers import Helpers

class PtMethods:
    def __init__(self, args):
        self.ptjsonlib           = ptjsonlib.PtJsonLib()
        self.headers             = ptnethelper.get_request_headers(args)
        self.proxies             = {"http": args.proxy, "https": args.proxy}
        self.use_json            = args.json
        self.redirects           = args.redirects
        self.cache               = args.cache
        self.timeout             = args.timeout
        self.show_headers        = args.show_headers
        self.show_response       = args.show_response
        self.check_basic_methods = args.check_basic_methods

        self.http_client         = http_client.HttpClient(args, self.ptjsonlib)
        self.helpers = Helpers(args, self.ptjsonlib, self.http_client)

        try:
            self.url_list = ptmisclib.read_file(args.file) if args.file else args.url
        except FileNotFoundError:
            self.ptjsonlib.end_error("File not found", self.use_json)

        if len(self.url_list) > 1 and self.use_json:
            self.ptjsonlib.end_error("Cannot test more than 1 URL while --json parameter is present", self.use_json)

    def run(self):
        for index, url in enumerate(self.url_list):
            try:
                self.port, url      = self._parse_url(url)
                ptprinthelper.ptprint(f"Testing: {url}", "TITLE", not self.use_json, colortext=True)
                options: list       = self._get_options(url)
                methods: dict       = self._check_methods(url)
                connect_test: bool  = self._check_connect_method(url)
                proxy_test: bool    = self._check_proxy_method(url)

                self._print_results(url, options, methods, proxy_test, connect_test)

            except (requests.exceptions.RequestException, ValueError, Exception) as e:
                if len(self.url_list) > 1:
                    ptprinthelper.ptprint(f"Error: {e}", "ERROR", not self.use_json, end="\n\n" if not index+1 == len(self.url_list) else "\n")
                    continue
                else:
                    self.ptjsonlib.end_error(f"{e}", self.use_json)

        if self.use_json:
            self.ptjsonlib.set_status("finished")
            ptprinthelper.ptprint(self.ptjsonlib.get_result_json(), "", self.use_json)

    def _check_connect_method(self, url):
        try:
            response = self._get_response("https://www.example.com", "GET", proxies={"https": url+":"+self.port})
        except requests.RequestException as e:
            return False
        if re.search(r"<title>Example Domain</title>", response.text):
            try:
                response_localhost = self._get_response("https://127.0.0.1", "GET", {"https": url+":"+self.port})
                title = re.search(r"<title.*?>([\s\S]*?)</title>", response_localhost.text)
                title = title.groups()[0] if title else title
                return title
            except requests.RequestException as e:
                title = "Error retrieving title from localhost"
                return title

    def _check_proxy_method(self, url):
        try:
            r, response_dump = self._get_response(url="http://www.example.com", method="GET", proxies={"http": f"{url}:{self.port}"}, dump_response=True)
        except requests.RequestException as e:
            return False

        if re.search(r"<title>Example Domain</title>", r.text):
            try:
                response_localhost = self._get_response("http://127.0.0.1", "GET", {"http": f"{url}:{self.port}"})
            except requests.RequestException as e:
                title = "Error retrieving title from localhost"
                return title
            title = re.search(r"<title.*?>([\s\S]*?)</title>", response_localhost.text)
            if title:
                title = title.groups()[0]
            self.ptjsonlib.add_vulnerability("PTWVPROXY", vuln_request=response_dump["request"], vuln_response=response_dump["response"], note=f"Title of localhost when proxy is used: {title}")
            return title

    def _get_options(self, url):
        try:
            response = self._get_response(url, "OPTIONS")
            if "Allow" in response.headers:
                allowed_methods = response.headers["Allow"].split(", ")
                return allowed_methods
            else:
                return ["None"]
        except requests.exceptions.RequestException as e:
            return ["error"]

    def _check_methods(self, url):
        """Check url for available methods"""
        methods_result = {"available_methods": [], "not_available_methods": []}
        for method in ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD", "TRACE", "DEBUG", "FOO"]:
            ptprinthelper.ptprint(f"Testing method: {method} {' '*10}", "TITLE", self.use_json == False, end="\r")
            try:
                response, response_dump = self._get_response(url, method, dump_response=True)
            except requests.RequestException as e:
                methods_result["not_available_methods"].append({"method": method, "status": 'error', "location": None, "headers": [], "response": []})
                continue
            method_data = {"method": method, "status": response.status_code, "location": None, "headers": [], "response": []}
            if response.headers.get("location"):
                method_data.update({"location": response.headers.get("location")})
            if self.show_headers:
                method_data["headers"].append(dict(response.headers))
            if self.show_response:
                method_data["response"].append(response.text)
            if response.status_code < 400:
                methods_result["available_methods"].append(method_data)

                if self.use_json:
                    if self.check_basic_methods:
                        vuln_code_map = {"PUT": "PTV-WEB-HTTP-METPUT", "PATCH": "PTV-WEB-HTTP-METPTCH", "DELETE": "PTV-WEB-HTTP-METDEL", "OPTIONS": "PTV-WEB-HTTP-METOPT", "HEAD": "PTV-WEB-HTTP-METHEAD", "TRACE": "PTV-WEB-HTTP-METTRC", "DEBUG": "PTV-WEB-HTTP-METDBG", "FOO": "PTV-WEB-HTTP-METNON"}
                        if vuln_code_map.get(method):
                            self.ptjsonlib.add_vulnerability(vuln_code_map[method])
                        self.handle_check_basic_methods(method)
                    else:
                        node = self.ptjsonlib.create_node_object("httpMethod", properties={"name": method, "httpMethodType": method})
                        if method == "TRACE":
                            node["vulnerabilities"].append({"vulnCode": "PTV-WEB-HTTP-METTRC"})
                        self.ptjsonlib.add_node(node)
            else:
                methods_result["not_available_methods"].append(method_data)
        ptprinthelper.ptprint(f"{' '*30}", "", self.use_json == False, end="\r")

        return methods_result

    def _print_results(self, url, options, methods, proxy_method, connect_method):
        ptprinthelper.ptprint(f"Response for OPTIONS: {', '.join(options)}", "INFO", self.use_json == False)

        for key, value in methods.items():
            ptprinthelper.ptprint(f"{key.capitalize().replace('_',' ')}:", "INFO", self.use_json == False, newline_above=True)
            if not value:
                ptprinthelper.ptprint(f"    None", "", self.use_json == False)
            for dictionary in value:
                ptprinthelper.ptprint(f"    {dictionary['method']}{' '*(9-len(dictionary['method']))}[{dictionary['status']}]", "", self.use_json == False, "")
                if dictionary["location"]:
                    ptprinthelper.ptprint(f"        -> {dictionary['location']}", "", self.use_json == False)
                else:
                    ptprinthelper.ptprint(f" ", "", self.use_json == False, end="\n")
                if self.show_headers:
                    for header, value in dictionary["headers"][0].items():
                        ptprinthelper.ptprint(f'      {header} : {value}', 'ADDITIONS', self.use_json == False, colortext=True)
                if self.show_headers and self.show_response:
                    ptprinthelper.ptprint(f" ", "", self.use_json == False)
                if self.show_response:
                    ptprinthelper.ptprint(f'{"".join(dictionary["response"])}', 'ADDITIONS', self.use_json == False, colortext=True)

        ptprinthelper.ptprint(f" ", "", self.use_json == False)
        if proxy_method:
            ptprinthelper.ptprint(f"Proxy mode is allowed", "VULN", self.use_json == False)
            ptprinthelper.ptprint(f"Title of localhost via proxy: {proxy_method}", "VULN", self.use_json == False)
        else:
            ptprinthelper.ptprint(f"Proxy mode is not allowed", "NOTVULN", self.use_json == False)

        if connect_method:
            ptprinthelper.ptprint(f"CONNECT method at port {self.port} is allowed", "VULN", self.use_json == False)
            ptprinthelper.ptprint(f"Title of localhost via CONNECT method: {connect_method}", "VULN", self.use_json == False)
        else:
            ptprinthelper.ptprint(f"CONNECT method at port {self.port} is not allowed", "NOTVULN", self.use_json == False)

        if next((method for method in methods["available_methods"] if method['method'] == "TRACE"), None):
            ptprinthelper.ptprint(f"TRACE method is allowed", "VULN", self.use_json == False)

        if len(self.url_list) > 1 and not url == self.url_list[-1]:
            ptprinthelper.ptprint(f" ", "", self.use_json == False)

    def _get_response(self, url, method, proxies=None, dump_response=False):
        """Retrieve response"""
        if proxies is None:
            proxies = self.proxies
        return ptmisclib.load_url_from_web_or_temp(url, method=method, headers=self.headers, proxies=proxies, timeout=self.timeout, redirects=self.redirects, verify=False, cache=self.cache, dump_response=dump_response)

    def _parse_url(self, url):
        """Validates url, returns port and url"""
        o = urllib.parse.urlparse(url)
        if o.scheme not in ["http", "https"]:
            raise ValueError("Missing or unsupported schema")
        if ":" in o.netloc:
            split_obj = o.netloc.split(":")
            port = split_obj[-1]
            #o = o._replace(netloc=split_obj[0])
        else:
            port = "443" if o.scheme == "https" else "80"

        # check if path to valid file, else get static file from response
        if not o.path or o.path == "/" or not os.path.basename(o.path).count('.'):
            response = self.helpers._find_static_resource(url)
            return port, response.url if response else url

        return port, urllib.parse.urlunparse(o)


def get_help():
    return [
        {"description": ["HTTP Methods Testing Tool"]},
        {"usage": ["ptmethods <options>"]},
        {"Tip": ["Use this script against existing sources like homepages, images, or resources protected by HTTP authentication."]},
        {"usage_example": [
            "ptmethods -u https://www.example.com/image.png",
            "ptmethods -u https://www.example.com/index.php",
            "ptmethods -u https://www.example.com/index.php -c PHPSESSID=abcdef",
            "ptmethods -f urlList.txt",
        ]},
        {"options": [
            ["-u",  "--url",                    "<url>",            "Test specified URL"],
            ["-f",  "--file",                   "<file>",           "Load URLs from file"],
            ["-sh", "--show-headers",           "",                 "Show response headers"],
            ["-sr", "--show-response",          "",                 "Show response text"],
            ["-T",  "--timeout",                "",                 "Set timeout (default 10)"],
            ["-p",  "--proxy",                  "<proxy>",          "Set proxy (e.g. http://127.0.0.1:8080)"],
            ["-ua", "--user-agent",             "<ua>",             "Set User-Agent header"],
            ["-c",  "--cookie",                 "<cookie>",         "Set cookie"],
            ["-H",  "--headers",                "<header:value>",   "Set custom header(s)"],
            ["-r",  "--redirects",              "",                 "Follow redirects (default False)"],
            ["-c",  "--cache",                  "",                 "Cache requests (load from tmp in future)"],
            ["-b",  "--check-basic-methods",    "",                 "Skip creating JSON nodes (used with --json option)"],
            ["-v",  "--version",                "",                 "Show script version and exit"],
            ["-h",  "--help",                   "",                 "Show this help message and exit"],
            ["-j",  "--json",                   "",                 "Output in JSON format"],
        ]
        }]


def parse_args():
    parser = argparse.ArgumentParser(add_help=False, usage="ptmethods <options>")
    exclusive_group = parser.add_mutually_exclusive_group(required=True)
    exclusive_group.add_argument("-u", "--url",         type=str, nargs="+")
    exclusive_group.add_argument("-f", "--file",        type=str)
    parser.add_argument("-p",  "--proxy",               type=str)
    parser.add_argument("-ua", "--user-agent",          type=str, default="Penterep Tools")
    parser.add_argument("-c",  "--cookie",              type=str, nargs="+")
    parser.add_argument("-T",  "--timeout",             type=int, default=6)
    parser.add_argument("-H",  "--headers",             type=ptmisclib.pairs, nargs="+")
    parser.add_argument("-j",  "--json",                action="store_true")
    parser.add_argument("-r",  "--redirects",           action="store_true")
    parser.add_argument("-C",  "--cache",               action="store_true")
    parser.add_argument("-b",  "--check-basic-methods", action="store_true")
    parser.add_argument("-sr", "--show-response",       action="store_true")
    parser.add_argument("-sh", "--show-headers",        action="store_true")
    parser.add_argument("-v",  "--version",             action="version", version=f"{SCRIPTNAME} {__version__}")

    parser.add_argument("--socket-address",          type=str, default=None)
    parser.add_argument("--socket-port",             type=str, default=None)
    parser.add_argument("--process-ident",           type=str, default=None)


    if len(sys.argv) == 1 or "-h" in sys.argv or "--help" in sys.argv:
        ptprinthelper.help_print(get_help(), SCRIPTNAME, __version__)
        sys.exit(0)

    args = parser.parse_args()
    ptprinthelper.print_banner(SCRIPTNAME, __version__, args.json, space=0)
    return args


def main():
    global SCRIPTNAME
    SCRIPTNAME = "ptmethods"
    requests.packages.urllib3.disable_warnings()
    args = parse_args()
    script = PtMethods(args)
    script.run()


if __name__ == "__main__":
    main()

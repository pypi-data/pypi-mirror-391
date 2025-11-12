#!/usr/bin/python3
"""
    Copyright (c) 2025 Penterep Security s.r.o.

    ptmultifinder is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ptmultifinder is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of

    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ptmultifinder.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import os
import socket
import sys; sys.path.append(__file__.rsplit("/", 1)[0])
import json
import requests
import re
import warnings

from typing import List
from _version import __version__

from ptlibs.http.http_client import HttpClient
from ptlibs import ptjsonlib, ptmisclib, ptprinthelper, ptnethelper, tldparser, sockets
from ptlibs.threads import ptthreads, printlock
from threading import Lock


from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse


class PtMultiFinder:
    def __init__(self, args):
        self.ptjsonlib = ptjsonlib.PtJsonLib()
        self.ptthreads = ptthreads.PtThreads()
        self.headers   = ptnethelper.get_request_headers(args)
        self.use_json  = args.json
        self.timeout   = args.timeout if not args.proxy else None
        self.args      = args
        self.proxies   = {"http": args.proxy, "https": args.proxy}
        self.sources   = self._get_sources(args.source)
        self.domains   = self._get_domains(args.domains)
        self.case_flag = 0 if self.args.case_sensitive else re.IGNORECASE
        self.http_client = HttpClient(args=self.args, ptjsonlib=self.ptjsonlib)

        self._output_file = open(self.args.output, "a", buffering=1, encoding="utf-8") if self.args.output else None

        if len(self.domains) > 1 and self.use_json:
            self.ptjsonlib.end_error(f"Cannot test more than 1 domain while --json parameter is present", self.use_json)

    def run(self, args):
        ptprinthelper.ptprint("Positive targets:", "TITLE", not self.use_json, colortext=True)

        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            future_to_domain = {executor.submit(self.check_domains, domain): domain for domain in self.domains}
            for future in as_completed(future_to_domain):
                domain = future_to_domain[future]
                try:
                    future.result()
                except Exception as e:
                    pass

    def check_domains(self, domain: str):
        """Threaded check domain method"""
        url = self._normalize_domain(domain)
        if self.args.check:
            if self._check_status_of_non_existing_resource(url):
                return

        for file_path in self.sources:
            full_url = f"{url}/{file_path}" if file_path else url
            ptprinthelper.ptprint(f"{full_url}", "ADDITIONS", not self.use_json, end="\r", flush=True, colortext=True, clear_to_eol=True) # Current tested URL
            self._test_url(full_url)

    def _normalize_domain(self, domain: str) -> str:
        """Ensure the domain has an HTTPS scheme."""
        if not re.match(r'^https?://', domain):
            return 'https://' + domain
        return domain

    def _check_status_of_non_existing_resource(self, url: str) -> bool:
        """Check a non-existing resource to see if the domain is responding as expected."""
        try:
            response = self.http_client.send_request(f"{url}/f00B4rN0tF0und", method="GET", allow_redirects=self.args.redirects, timeout=self.timeout, proxies=self.proxies, verify=False, headers=self.headers, max_retries=self.args.max_retries)
            if response.status_code in (200, 301, 302):
                return True
        except Exception as e:
            return False

    def _is_same_domain_redirect(self, original_url: str, redirect_url: str) -> bool:
        """Check if the redirect URL is within the same domain."""
        if not redirect_url:
            return
        original_netloc = urlparse(original_url).netloc
        redirected_netloc = urlparse(redirect_url).netloc
        return original_netloc.split('.')[-2:] == redirected_netloc.split('.')[-2:]

    def _get_base_domain(self, url: str) -> str:
        """Extract the base domain from a URL (including scheme but excluding path)."""
        parsed_url = urlparse(url)
        return f"{parsed_url.scheme}://{parsed_url.netloc}"

    def _test_url(self, url: str) -> bool:
        try:
            response = self.http_client.send_request(url, method="GET", allow_redirects=self.args.redirects, timeout=self.timeout, proxies=self.proxies, verify=False, headers=self.headers, max_retries=self.args.max_retries)
        except:
            return False

        if response.status_code not in self.args.status_code:
            return False

        if "window.location=" in response.text.lower():
            return False

        if self.proxies and "burp" in response.text.lower():
            return False

        if self.args.without_path:
            url = urlunparse((parsed.scheme, parsed.netloc, '', '', '', ''))

        if self.args.without_scheme:
            url = url.split("://")[-1]

        if self.args.string_yes and any(re.search(string, response.text, self.case_flag) for string in self.args.string_yes):
            self.print_url(url)
            #ptprinthelper.ptprint(f"{url}", "TEXT", not self.use_json, colortext=True, flush=True, clear_to_eol=True, filehandle=self._output_file)

        if self.args.string_no and not all(re.search(string, response.text, self.case_flag) for string in self.args.string_no):
            #self.print_url(url)

            ptprinthelper.ptprint(f"{url}", "TEXT", not self.use_json, colortext=True, flush=True, clear_to_eol=True, filehandle=self._output_file)

        if not self.args.string_yes and not self.args.string_no:
            self.print_url(url)
            #ptprinthelper.ptprint(url, "TEXT", not self.use_json, colortext=True, flush=True, clear_to_eol=True, filehandle=self._output_file)

        #if self.args.output and self._output_file:

        return True

    def print_url(self, url):
        ptprinthelper.ptprint(
            f"{url}",
            "TEXT",
            not self.use_json,
            colortext=True,
            flush=True,
            clear_to_eol=True,
            filehandle=self._output_file
        )

    def _get_sources(self, sources: List[str]):
        """Process sources (file to test)"""
        if len(sources) == 1 and os.path.isfile(sources[0]): # Process sources from file
            with open(os.path.abspath(sources[0]), "r") as source_file:
                return [line.strip() for line in source_file.readlines()]
        else: # Process sources from CLI
            return [source for source in sources]

    def _get_domains(self, domains: List[str]):
        """Process domains (from file or list)"""
        if len(domains) == 1 and os.path.exists(domains[0]): # Load domains from file
            with open(os.path.abspath(domains[0]), "r") as domain_file:
                loaded_domains = [line.strip() for line in domain_file.readlines()]
            return loaded_domains
        else:  # Process domains from list
            return domains

def get_help():
    return [
        {"usage": ["ptmultifinder <options>"]},
        {"usage_example": [
            "ptmultifinder --domains domains.txt --sources sources.txt",
            "ptmultifinder --domains domains.txt --sources admin.php .git/ backup/"
        ]},
        {"options": [
            ["-d",       "--domains",      "<domains>",                     "Domains or file with domains to test"],
            ["-s",       "--source",       "<source>",                      "Sources or file with sources to check"],
            ["-sc",      "--status-code",  "<status-code>",                 "Process only servers that respond with provided status codes (default 200)"],
            ["-sy",      "--string-yes",   "<string>",                      "Show only results that contain the specified string in the response"],
            ["-sn",      "--string-no",    "<string>",                      "Show only results that do not contain the specific string in the response"],
            ["-cs",      "--case-sensitive",    "",                         "Enable case sensitivity for -sy, -sn options"],
            ["-ch",      "--check",        "",                              "Skip domain if it responds with a status code of 200 to a non-existent resource."],
            ["-C",       "--cache",        "",                              "Enable caching of requests"],
            ["-r",       "--redirects",        "",                          "Follow redirects"],
            ["-mr",       "--max-retries",        "",                       "Set the number of retries on network connection failure. (default 0)"],
            ["-ws",       "--without-scheme",        "",                    "Output findings without scheme"],
            ["-wp",       "--without-path",        "",                      "Output findings without path"],
            ["-p",       "--proxy",        "<proxy>",                       "Set Proxy"],
            ["-a",       "--user-agent",   "<agent>",                       "Set User-Agent"],
            ["-t",       "--threads",      "<threads>",                     "Set Threads count"],
            ["-T",       "--timeout",      "<timeout>",                     "Set Timeout (default 5s)"],
            ["-H",       "--headers",      "<header:value>",                "Set custom headers"],
            ["-v",       "--version",      "",                              "Show script version and exit"],
            ["-h",       "--help",         "",                              "Show this help message and exit"],
            ["-j",       "--json",         "",                              "Output in JSON format"],
        ]
        }]

def valid_output_path(path: str) -> str:
    # Reject if it points to an existing directory
    if os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"'{path}' is a directory, not a file.")

    # Check if directory exists
    dir_name = os.path.dirname(os.path.abspath(path)) or "."
    if not os.path.exists(dir_name):
        raise argparse.ArgumentTypeError(f"Directory '{dir_name}' does not exist.")

    # Check filename validity
    filename = os.path.basename(path)

    # Example: Windows-safe filename check (for cross-platform safety)
    invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'
    if re.search(invalid_chars, filename):
        raise argparse.ArgumentTypeError(f"'{filename}' contains invalid characters.")

    # Optional: forbid empty or extensionless filenames
    if not filename.strip():
        raise argparse.ArgumentTypeError("Filename cannot be empty.")

    return path

def parse_args():
    parser = argparse.ArgumentParser(add_help=False, usage=f"{SCRIPTNAME} <options>")
    parser.add_argument("-d",  "--domains",     type=str, nargs="+", required=True)
    parser.add_argument("-s",  "--source",      type=str, nargs="*", default=[""])
    parser.add_argument("-sc", "--status-code", type=int, nargs="*", default=[200])
    parser.add_argument("-sy", "--string-yes",  type=str, nargs="+")
    parser.add_argument("-sn", "--string-no",   type=str, nargs="+")
    parser.add_argument("-a",  "--user-agent",  type=str, default="Penterep Tools")
    parser.add_argument("-H",  "--headers",     type=ptmisclib.pairs, nargs="+")
    parser.add_argument("-t",  "--threads",     type=int, default=100)
    parser.add_argument("-T",  "--timeout",     type=int, default=5)
    parser.add_argument("-p",  "--proxy",       type=str)
    parser.add_argument("-o",  "--output",       type=valid_output_path)

    parser.add_argument("-mr",  "--max-retries",     type=int, default=0)
    parser.add_argument("-ws",  "--without-scheme",action="store_true")
    parser.add_argument("-ws",  "--without-path",action="store_true")
    parser.add_argument("-cs", "--case_sensitive", action="store_true")
    parser.add_argument("-C",  "--cache",          action="store_true")
    parser.add_argument("-j",  "--json",           action="store_true")
    parser.add_argument("-ch", "--check",          action="store_true")
    parser.add_argument("-r", "--redirects",       action="store_true")
    parser.add_argument("-v",  "--version",        action="version", version=f"%(prog)s {__version__}")

    parser.add_argument("--socket-address",  type=str, default=None)
    parser.add_argument("--socket-port",     type=str, default=None)
    parser.add_argument("--process-ident",   type=str, default=None)

    if len(sys.argv) == 1 or "-h" in sys.argv or "--help" in sys.argv:
        ptprinthelper.help_print(get_help(), SCRIPTNAME, __version__)
        sys.exit(0)
    args = parser.parse_args()
    print(args.output)

    if not args.source:
        args.source = [""]

    ptprinthelper.print_banner(SCRIPTNAME, __version__, args.json, 0)
    return args


def main():
    global SCRIPTNAME
    SCRIPTNAME = "ptmultifinder"
    args = parse_args()
    script = PtMultiFinder(args)
    # Suppress all warnings
    warnings.filterwarnings("ignore")
    script.run(args)

if __name__ == "__main__":
    main()

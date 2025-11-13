import re
from urllib.parse import urlparse, urlunparse

from ptlibs.ptprinthelper import ptprint


class Helpers:
    def __init__(self, args: object, ptjsonlib: object, http_client: object):
        """
        Helpers provides utility methods for loading definition files
        and making HTTP requests in a consistent way across modules.
        """
        self.args = args
        self.ptjsonlib = ptjsonlib
        self.http_client = http_client

    def fetch(self, url, allow_redirects=False):
        """
        Sends an HTTP GET request to the specified URL.

        Args:
            url (str): URL to fetch.
            allow_redirects (bool, optional): Whether to follow redirects. Defaults to False.

        Returns:
            Response: The HTTP response object.
        """

        if self.args.redirects:
            redirects = True
        else:
            redirects = allow_redirects

        try:
            response = self.http_client.send_request(
                url=url,
                method="GET",
                headers=self.args.headers,
                allow_redirects=redirects,
                timeout=self.args.timeout
            )
            return response

        except Exception as e:
            return None

    def _find_static_resource(self, url):
        """
        Locate a static resource to test:
        1) Try '/favicon.ico'.
        2) If not found, download the homepage HTML and search for the first
            reference to a static asset (.js, .css, .png, .jpg, .jpeg, .gif, .ico).

        Returns:
            response or None: response (requests.Response) if a resource is found, else None.
        """
        parsed = urlparse(url)
        base = urlunparse((parsed.scheme, parsed.netloc, "", "", "", "")) #self.args.url.rstrip('/')

        parsed_base = urlparse(base)
        favicon = base + '/favicon.ico'
        resp = self.fetch(favicon)

        if resp is not None:
            if resp.status_code in (301, 302):
                #ptprint(f"Redirect detected to {resp.headers.get('Location')}", "INFO", not self.args.json, indent=4)
                return None
            elif resp.status_code == 200:
                return resp

        resp_home = self.fetch(base + '/')

        if resp_home is not None:
            if resp_home.status_code in (301, 302):
                #ptprint(f"Redirect to {resp_home.headers.get('Location')}","INFO", not self.args.json, indent=4)
                return None
            elif resp_home.status_code != 200:
                #ptprint(f"Homepage returned {resp_home.status_code}","INFO", not self.args.json, indent=4)
                return None
        else:
            #ptprint("Connection error occurred", "INFO", not self.args.json, indent=4)
            return None


        html = resp_home.text or ''
        for match in re.finditer(
            r'(?:href|src)=["\']([^"\']+\.(?:js|css|png|jpg|jpeg|gif|ico))["\']',
            html,
            re.IGNORECASE,
        ):
            candidate_url = urljoin(base + '/', match.group(1))
            if urlparse(candidate_url).netloc != parsed_base.netloc:
                continue

            r = self.fetch(candidate_url)
            if r is not None:
                if r.status_code == 200:
                    return r
        return None
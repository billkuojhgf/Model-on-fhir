import json
import configparser

from time import sleep
from urllib import parse
from urllib.parse import urljoin

import jmespath
import requests

config = configparser.ConfigParser()
config.read("../config.ini")

# Fixed variables
COMMAND = '/Patient/$export'
RESOURCES = [
    "Patient",
    "Group"
]
HEADERS = {
    'Accept': 'application/fhir+json',
    'Prefer': 'respond-async',
}
VALID_QUERY_PARAMS = [
    '_outputFormat',
    '_since',
    '_type',
]
MANIFEST_URLS = jmespath.compile('output[*].url')
SERVER_URLS = config['bulk_server']['BULK_SERVER_URL']


class BulkDataClient(object):
    manifest = []

    @property
    def provisioned(self):
        return bool(self.manifest)

    def __init__(
            self,
            server=SERVER_URLS):
        self.server = server
        self.session = requests.Session()
        self.session.headers = HEADERS

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def _issue(self, url, **params):
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response

    def provision(self, compartment=None, **query_params):
        # TODO 3 options: /$export, /Group/[id]/$export, /Patient/$export
        params = {
            k: v for (k, v) in query_params.items()
            if k in VALID_QUERY_PARAMS
        }
        response = self._issue(self.server + COMMAND, **params)
        content = response.headers.get('Content-Location')
        # NOTE `content` should be an absolute URL, but we're being kind :)
        try:
            assert parse.urlparse(content).scheme
        except AssertionError:
            content = urljoin(self.server, content)
        while True:
            # TODO backoff
            # TODO would be a good place for asyncio
            sleep(0.5)
            response = self._issue(content)
            if response.status_code == 200:
                self.manifest = MANIFEST_URLS.search(response.json())
                return

    def iter_json(self):
        if not self.provisioned:
            return
        for url in self.manifest:
            data = self._issue(url)
            for item in data.iter_lines():
                return json.loads(item)


if __name__ == "__main__":
    bulk_server = BulkDataClient()
    bulk_server.provision()
    print(bulk_server.iter_json())
    pass

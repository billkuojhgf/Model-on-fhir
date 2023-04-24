import json

from config import configObject as config
from time import sleep
from urllib import parse
from urllib.parse import urljoin

import ndjson
import base64
import jmespath
import requests


# Fixed variables
COMMAND = '/$export'
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
        retry_time = 0
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
            try:
                response = self._issue(content)
            except requests.exceptions.ReadTimeout as e:
                if retry_time > 10:
                    print("Retry times exceeded 10, aborting...")
                    raise e

                retry_time += 1
                print(f"Request timed out, retrying... \nTried times: {retry_time}")
                continue

            if response.status_code == 200:
                self.manifest = MANIFEST_URLS.search(response.json())
                return

    def iter_ndjson_dict(self) -> {str: list} or None:
        if not self.provisioned:
            return
        # return_data_dict = { "{data.resourceType}" : [data[0], data[1]... ] }
        return_data_dict = dict()
        for url in self.manifest:
            bulk_data_response = self._issue(url)
            bulk_data_base64 = str(json.loads(bulk_data_response.content)["data"])
            bulk_data_ndjson = base64.b64decode(bulk_data_base64)
            bulk_data_ndjson = ndjson.loads(bulk_data_ndjson)
            for bulk_data_json in bulk_data_ndjson:
                if bulk_data_json['resourceType'] not in return_data_dict:
                    return_data_dict[bulk_data_json['resourceType']] = []
                return_data_dict[bulk_data_json['resourceType']].append(bulk_data_json)

        return return_data_dict


if __name__ == "__main__":
    print("test")
    bulk_server = BulkDataClient()
    bulk_server.provision()
    ndj = bulk_server.iter_ndjson_dict()
    print("test")
    pass

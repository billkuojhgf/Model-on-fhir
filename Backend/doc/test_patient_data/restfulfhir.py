# -*- coding: utf-8 -*-

import os
import requests
import json


def create_resource(
        url,
        path
):
    session = requests.session()
    for fname in os.listdir(path):
        input_file = open(os.path.join(path, fname), encoding="utf-8")
        json_dict = json.load(input_file)
        id = None

        resources = json_dict['resourceType']
        try:
            id = json_dict['id']
        except KeyError:
            continue
        if id is not None:
            fhir_store_path = "{}/{}/{}/".format(
                url, resources, id
            )
        else:
            fhir_store_path = "{}/{}/".format(url, resources)

        headers = {"Content-Type": "application/fhir+json"}

        try:
            response = session.put(
                fhir_store_path, headers=headers, json=json_dict)
            # response.raise_for_status()
            resource = response.json()
            print("Created {} resource with ID {}".format(
                resources, resource["id"]))
        except Exception as e:
            print(e, id)
            continue


url = "http://ming-desktop.ddns.net:8192/fhir"
path = input("請輸入檔案夾路徑: ")
create_resource(url, path)

print("Done!")

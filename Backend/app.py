import csv
import importlib
from flask import Flask, jsonify, request, abort
from flask_cors import CORS

from base import feature_table
from base import patient_data_search as ds
from models import *

app = Flask(__name__)
CORS(app)

# Map the csv into dictionary
table = feature_table.FeatureTable("./config/features.csv")


@app.route('/', methods=['GET'])
def index():
    return "Hello, World!<br/><br/>請在網址列的/後面輸入你要搜尋的病患id即可得出結果<br/>Example: <a " \
           "href=\"/diabetes?id=test-03121002\">http://localhost:5000/diabetes?id=test-03121002</a> "


@app.route('/<api>', methods=['GET'])
def api_with_id(api):
    """

    :param api:<base>/<model name>?id=<patient's id>&hour_alive_format
    :return:
    """
    if request.values.get('id') is None:
        abort(400, description="Please fill in patient's ID.")
    else:
        patient_id = request.values.get('id')

    try:
        # collect patient's feature data from FHIR Server, the features are based on which api is calling.
        patient_data_dict = ds.model_feature_search_with_patient_id(
            patient_id, table.get_model_feature_dict(api), api)
    except KeyError:
        abort(400, description="Model was not found in system.")
    except Exception as e:
        abort(500, description=e)
    else:
        return return_model_result(patient_data_dict, api)


@app.route('/<api>/change', methods=['POST'])
# POST method will get the object body from frontend
# POST method will only return predict value(double or integer)
def api_with_post(api):
    patient_data_dict = request.get_json()
    return return_model_result(patient_data_dict, api)


def return_model_result(patient_data_dict, api):
    try:
        model_results = globals()[api].predict(patient_data_dict)
    except KeyError:
        abort(400, description="Model was not found in system.")
    except Exception as e:
        abort(500, description=e)
    else:
        patient_data_dict["predict_value"] = model_results
        return patient_data_dict


def main():
    print(globals()["diabetes"].predict())


if __name__ == '__main__':
    # main()
    app.debug = True
    app.run()

import csv
import importlib
from flask import Flask, jsonify, request, abort
from flask_cors import CORS

from base import FeatureTable
from base import patient_data_search as ds
from models import *

app = Flask(__name__)
CORS(app)

# Map the csv into dictionary
table = FeatureTable.FeatureTable("./config/features.csv")


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
        patient_data_dict = ds.model_feature_search_with_patient_id(
            patient_id, table.get_model_feature_dict(api), api)
        model_results = getattr(eval("{}".format(api)),
                                "predict")(patient_data_dict)
    except KeyError:
        abort(400, description="Model was not found in system.")
    except Exception as e:
        abort(500, description=e)
    else:
        return jsonify(return_model_result(patient_data_dict, api))


@app.route('/<api>/change', methods=['POST'])
# POST method will get the object body from frontend
# POST method will only return predict value(double or integer)
def api_with_post(api):
    patient_data_dict = request.get_json()
    return jsonify(return_model_result(patient_data_dict, api))


def return_model_result(patient_data_dict, api):
    try:
        model_results = getattr(eval("{}".format(api)),
                                "predict")(patient_data_dict)
    except KeyError:
        abort(400, description="Model was not found in system.")
    except Exception as e:
        abort(500, description=e)
    else:
        patient_data_dict["predict_value"] = model_results
        return patient_data_dict


def main():
    print(getattr(eval('diabetes'), 'predict')())


def import_model():
    # get a handle on the module
    mdl = importlib.import_module('models')

    # is there an __all__?  if so respect it
    if "__all__" in mdl.__dict__:
        names = mdl.__dict__["__all__"]
    else:
        # otherwise we import all names that don't begin with _
        names = [x for x in mdl.__dict__ if not x.startswith("_")]

    # now drag them in
    globals().update({k: getattr(mdl, k) for k in names})


if __name__ == '__main__':
    app.debug = True
    app.run()
    # main()

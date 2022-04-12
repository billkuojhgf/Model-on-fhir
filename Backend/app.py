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
        patient_data_dict["predict_value"] = model_results
        return patient_data_dict


@app.route('/<api>/change', methods=['POST'])
# POST method will get the object body from frontend
# POST method will only return predict value(double or integer)
def api_with_post(api):
    patient_data_dict = request.get_json()
    # if api == 'diabetes':
    #     predict_value = diabetes_model_result(request_dict)
    # elif api == 'qcsi':
    #     predict_value = qcsi_calc_with_score(request_dict)
    # elif api == 'rox':
    #     predict_value = rox_index_calc_with_score(request_dict)
    # else:

    # return "", 404
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


if __name__ == '__main__':
    app.debug = True
    app.run()
    # main()

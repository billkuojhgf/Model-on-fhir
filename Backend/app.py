import importlib

from flask import Flask
from flask import abort
from flask import jsonify
from flask import request
from flask_cors import CORS

mocab_app = Flask(__name__)
CORS(mocab_app)

from base import patient_data_search as ds
from base.object_store import feature_table
from base.model_input_transformer import transformer
from mocab_models import *
import smart_on_fhir

# Map the csv into dictionary
table = feature_table


@mocab_app.route('/', methods=['GET'])
def index():
    return "Hello, World!<br/><br/>請在網址列的/後面輸入你要搜尋的病患id即可得出結果<br/>Example: <a " \
           "href=\"/pima_diabetes?id=test-03121002\">http://localhost:5000/diabetes?id=test-03121002</a> "


@mocab_app.route('/exist_model')
def exist_model():
    return jsonify({"model": feature_table.get_exist_model_name()})


@mocab_app.route('/<api>', methods=['GET'])
def api_with_id(api):
    """
    Description:
        This api gets the request with patient's id and model, then the server would return the model's result
        and patient's data.

    :param api:<base>/<model name>?id=<patient's id>&hour_alive_format
    :return: json object
        {
            "predict_value": <int> or <double>
            "<feature's name>": {
                "date": YYYY-MM-DDThh:mm:ss,
                "value": <boolean> or <int> or <double> or <string> // depends on the data
            }
        }
    """
    # TODO: the hour_alive_time request value
    patient_id = request.values.get('id')
    if patient_id is None:
        abort(400, description="Please fill in patient's ID.")
    hour_alive_time = request.values.get('hour_alive_time')  # None if request has no hour_alive_time parameter

    patient_data_dict = ds.model_feature_search_with_patient_id(
        patient_id, table.get_model_feature_dict(api), data_alive_time=hour_alive_time)
    patient_data_dict["predict_value"] = return_model_result(patient_data_dict, api)
    return jsonify(patient_data_dict)


@mocab_app.route("/smart/<api>", methods=['GET'])
def smart_api_with_id(api):
    patient_id = request.values.get('id')
    if patient_id is None:
        abort(400, description="Please fill in patient's ID.")

    if not smart_on_fhir.check_auth():
        abort(401, description="SMART Auth is not enabled. Launch MoCab SMART Endpoint in EHR First.")

    patient_data_dict = ds.smart_model_feature_search_with_patient_id(
        patient_id, table.get_model_feature_dict(api))

    return jsonify(patient_data_dict)


def str2bool(string: str or None) -> bool:
    if type(string) is not str:
        return string

    true_string = ('true', '1', 't', 'y', 'yes', 'yeah', 'yup', "on")
    false_string = ('false', '0', 'f', 'n', 'no', 'nope', 'nan', 'off')
    if string.lower() in true_string:
        return True
    elif string.lower() in false_string:
        return False
    return abort(500, description=f"SMART parameter value unknown: {string}")


def verify_data(patient_data_dict, api):
    # MUST HAVE: 1. Keys with each feature. 2. Value with Dict type and has Key with the name "value".
    try:
        validation_table = table.get_model_feature_dict(api)
    except KeyError:
        raise KeyError("{} Model is not in the table".format(api))

    for key in validation_table.keys():
        if key not in patient_data_dict.keys():
            raise KeyError("{} was not given".format(key))

        if "value" not in patient_data_dict[key].keys():
            raise KeyError("{}'s value has no 'value' key.".format(key))


@mocab_app.route('/<api>/change', methods=['POST'])
# POST method will get the object body from frontend
# POST method will only return predict value(double or integer)
def api_with_post(api):
    """
    Description:
        This api gets the request with patient's data and model, then the server would return the model's result
        and patient's data.

    :param api: POST <base>/<model name>/change
    :return: json object
        {
            "predict_value": <int> or <double>
            "<feature's name>": {
                "date": YYYY-MM-DDThh:mm:ss,
                "value": <boolean> or <int> or <double> or <string> // depends on the data
            }
        }
    """
    patient_data_dict = request.get_json()
    verify_data(patient_data_dict, api)
    patient_data_dict["predict_value"] = return_model_result(patient_data_dict, api)
    return jsonify(patient_data_dict)


def return_model_result(patient_data_dict, api):
    """
        Function return_model_result會對 model執行 predict的動作，回傳 model的結果
        2022-10-10 新增一個新的動作：在丟入Model之前，會先將資料根據ModelFeature Table轉譯成model prefer的category
        TODO: 把return_model_result獨立成一個新的檔案，需要解決的技術難點: globals()[api]
    """

    # transfer patient data into model preferred input
    patient_data_list = transformer(patient_data_dict, api)
    model_results = globals()[api].predict(patient_data_list)
    return model_results


def import_model():
    # TODO: Need to figure out what actions does this function done, and optimize it.
    # get a handle on the module
    mdl = importlib.import_module('mocab_models')

    # is there an __all__?  if so respect it
    if "__all__" in mdl.__dict__:
        names = mdl.__dict__["__all__"]
    else:
        # otherwise we import all names that don't begin with _
        names = [x for x in mdl.__dict__ if not x.startswith("_")]

    # now drag them in
    globals().update({k: getattr(mdl, k) for k in names})


import_model()

if __name__ == "__main__":
    mocab_app.debug = True
    mocab_app.run()

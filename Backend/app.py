import os
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
        model_results = globals()[api].predict(patient_data_dict)
    except KeyError:
        abort(400, description="Model was not found in system.")
    except Exception as e:
        abort(500, description=e)
    else:
        patient_data_dict["predict_value"] = model_results
        return patient_data_dict


def main():
    names = []
    model_path = r"./models"
    for model_path_dir in os.listdir(model_path):
        # 阻絕 "__pycache__" folder
        if model_path_dir.startswith("_"):
            continue

        # 判斷該資料夾是否為 *符合條件* 的model
        """
            符合條件：
            欲新增的model都應該需要符合以下條件：
            1. folder名稱就是model的名稱
            2. 裡面有predict() function，負責做該model的predict，input attribute為patient_data_dict <type: dictionary>
            3. 該model會預設從model.py中去抓取predict function (方法： 預設是＿＿init__.py裡面會寫"from .model import predict")
               如果predict function不在model.py中，則需要修改__init__.py中的路徑
        """
        if os.path.isdir("{}/{}".format(model_path, model_path_dir)) and \
                os.path.exists("{}/{}/model.py".format(model_path, model_path_dir)):
            names.append(model_path_dir)

    models_init_file = open("./models/__init__.py", "w")
    models_init_file.write("__all__ = {}".format(names))
    models_init_file.close()


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
    main()
    import_model()
    app.debug = True
    app.run()


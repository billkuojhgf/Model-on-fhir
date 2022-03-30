import csv
from flask import Flask, jsonify, request
from flask_cors import CORS

from base.feature import *
from base.patient_data_search import *
from models import *

app = Flask(__name__)
CORS(app)

# Map the csv into dictionary
table = createTable()


@app.route('/', methods=['GET'])
def index():
    return "Hello, World!<br/><br/>請在網址列的/後面輸入你要搜尋的病患id即可得出結果<br/>Example: <a href=\"/diabetes?id=test-03121002\">http://localhost:5000/diabetes?id=test-03121002</a>"


@app.route('/<api>', methods=['GET'])
def api_with_id(api):
    if api == 'diabetes':
        if request.values.get('id'):
            id = request.values.get('id')
            yearsAliveTime = request.values.get(
                'yearAliveTime') if request.values.get('yearAliveTime') == True else 5
            dataAliveTime['years'] = yearsAliveTime
            diabetes.model.predict()
            return jsonify(diabetes_predict(id, table['diabetes'], dataAliveTime)), 200

    elif api == 'qcsi':
        if request.values.get('id'):
            id = request.values.get('id')
            hour_alive = request.values.get('hourAliveTime') if request.values.get(
                'hourAliveTime') == True else 24
            dataAliveTime['hours'] = hour_alive
            return jsonify(qcsi_calc_with_patient_id(id, table['qcsi'], dataAliveTime)), 200

    elif api == 'rox':
        if request.values.get('id'):
            id = request.values.get('id')
            hour_alive = request.values.get('hourAliveTime') if request.values.get(
                'hourAliveTime') == True else 24
            dataAliveTime['hours'] = hour_alive
            return jsonify(rox_index_calc_with_patient_id(id, table['rox'], dataAliveTime)), 200
    return "", 404


@app.route('/<api>/change', methods=['POST'])
# POST method will get the object body from frontend
# POST method will only return predict value(double or integer)
def api_with_post(api):
    request_dict = request.get_json()
    if api == 'diabetes':
        predict_value = diabetes_model_result(request_dict)
    elif api == 'qcsi':
        predict_value = qcsi_calc_with_score(request_dict)
    elif api == 'rox':
        predict_value = rox_index_calc_with_score(request_dict)
    else:
        return "", 404

    return {"predict_value": predict_value}, 200


if __name__ == '__main__':
    app.debug = True
    app.run()

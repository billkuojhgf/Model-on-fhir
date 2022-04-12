import joblib
import datetime
from base.searchsets import *


def diabetes_predict(patient_id, table, default_time=None):
    # default_time變數是為模型訓練用(type=date or datetime)，數值放入patient得病的時間，None表示使用現在時間`
    if default_time is None:
        default_time = datetime.datetime.now()

    # put all the resource we need in data
    data = dict()
    for key in table:
        data[key] = dict()
        data[key] = get_resources(patient_id, table[key], default_time)
    data['age'] = get_age(patient_id, default_time)

    # Put all the result and datas into result_dict and return as json format
    result_dict = dict()

    for key in data:
        result_dict[key] = dict()
        result_dict[key]['date'] = get_resource_datetime(
            data[key], default_time)
        result_dict[key]['value'] = get_resource_value(data[key])
    # get model result
    result_dict['predict_value'] = predict(result_dict)
    return result_dict


def predict(data: dict):
    # @data comes from two places, one is from diabetes_predict(), the other is from flask(not sure where yet).
    # data allows two kind of value set, one is dictionary(the value returned from get_resources()),
    #   another is value(the value comes from frontend)
    # Put all the values into temp and get ready to predict
    x = list()
    # fixed variable: pregnancies=6, skinthickness=35, diabetespedigreefunction=0.627
    # controlled variable: glucose, diastolic blood pressure, insulin, height, weight, age

    # TODO: get_age要重做，想一個好的辦法來處理這種例外情節
    temp = [6, data['glucose']['value'], data['diastolic blood pressure']['value'], 35, data['insulin']['value'],
            bmi(data['height']['value'], data['weight']['value']), 0.627, 72]
    loaded_model = joblib.load("./models/diabetes/finalized_model.sav")
    x.append(temp)
    result = loaded_model.predict_proba(x)
    # result = [no's probability, yes's probability]
    # return negative's probability
    return result[:, 1][0]


def bmi(height, weight):
    # weight(unit: kilogram)/ height(unit: meter)/ height(unit: meter)
    # weight = {
    #     'kg': weight_resource.valueQuantity.value,
    #     'g': weight_resource.valueQuantity.value / 1000,
    #     '[lb_av]': weight_resource.valueQuantity.value * 0.45359237
    # }.get(weight_resource.valueQuantity.unit, 0)
    # height = {
    #     'cm': height_resource.valueQuantity.value / 100,
    #     '[in_i]': height_resource.valueQuantity.value * 0.0254,
    # }.get(height_resource.valueQuantity.unit, 0)

    return float(weight) / float(height) / float(height)

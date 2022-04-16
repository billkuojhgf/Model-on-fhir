import datetime
from base.searchsets import *


def predict(patient_data_dict: dict):
    result_dict = patient_data_dict
    result_dict = convert_qcsi_value(result_dict)
    result_dict['predict_value'] = qcsi_model_result(result_dict)
    return result_dict


# qCSI Patient's id api
def qcsi_calc_with_patient_id(patient_id, table, dataAliveTime):
    # default_time變數是為模型訓練用, 這裡不需要這種東西
    default_time = datetime.datetime.now()

    # prepare all the patient's data to search
    # put all the resource we need in data
    data = dict()
    for key in table:
        data[key] = dict()
        data[key] = get_resources(
            patient_id, table[key], default_time, data_alive_time=dataAliveTime)

    # Put all datas into result_dict
    result_dict = dict()
    for key in data:
        result_dict[key] = dict()
        result_dict[key]['date'] = get_resource_datetime(
            data[key], default_time)
        result_dict[key]['value'] = get_resource_value(data[key])

    # convert the value into qcsi's value format
    result_dict = convert_qcsi_value(result_dict)
    # calculate the score of qcsi_covid
    result_dict['predict_value'] = qcsi_model_result(result_dict)
    return result_dict


# qCSI score api
def qcsi_calc_with_score(dict):
    result_dict = dict
    result_dict = convert_qcsi_value(result_dict)
    result_dict['predict_value'] = qcsi_model_result(result_dict)
    return result_dict


def qcsi_model_result(dict):
    result = 0
    for key in dict:
        result += dict[key]['value']
    # type(result) === int
    return result


def convert_qcsi_value(dict):
    for key in dict:
        dict[key]['value'] = {
            'respiratory rate': 0 if dict[key]['value'] <= 22 else 2 if dict[key]['value'] >= 28 else 1,
            'pulse oximetry': 5 if dict[key]['value'] <= 88 else 0 if dict[key]['value'] > 92 else 2,
            'o2 flow rate': 0 if dict[key]['value'] <= 2 else 5 if dict[key]['value'] >= 5 else 4
        }.get(key)
    return dict

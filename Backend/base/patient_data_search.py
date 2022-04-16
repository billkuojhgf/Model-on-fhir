import datetime
from base.searchsets import *  # fs: fhir server search


def model_feature_search_with_patient_id(id, table, model_name):
    default_time = datetime.datetime.now()

    data = dict()
    for key in table:
        data[key] = dict()
        try:
            data[key] = get_resources(id, table[key], default_time)
        except ResourceNotFound:
            data[key] = table['']

    result_dict = dict()
    for key in data:
        result_dict[key] = dict()
        result_dict[key]['date'] = get_resource_datetime(
            data[key], default_time)
        result_dict[key]['value'] = get_resource_value(data[key])

    return result_dict

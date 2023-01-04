import datetime

from base.search_sets import get_patient_resources
from base.search_sets import get_resource_datetime_and_value


def model_feature_search_with_patient_id(patient_id: str,
                                         table: dict,
                                         smart_enable: bool = False,
                                         default_time: str = None,
                                         data_alive_time: str = None) -> dict:
    if default_time is None:
        default_time = datetime.datetime.now()

    data = dict()
    for key in table:
        data[key] = dict()
        # If the search came from
        if smart_enable:
            data[key]['data_sets'], data[key]['data'] = \
                get_patient_resources(patient_id, table[key], default_time, data_alive_time, smart_enable)
        else:
            data[key]['data'] = get_patient_resources(patient_id, table[key], default_time, data_alive_time)

    result_dict = dict()
    for data_key in data:
        result_dict[data_key] = dict()
        # get_resource_datetime_and_value returns two values, date & value.
        # for other purpose, use other functions instead
        result_dict[data_key]['date'], result_dict[data_key]['value'] = get_resource_datetime_and_value(
            data[data_key]['data'], default_time
        )
        if smart_enable:
            result_dict[data_key]['dataSet'] = extract_data_in_data_sets(data[data_key], default_time)
    return result_dict


def extract_data_in_data_sets(data_sets, default_time) -> list:
    result_list = []
    sets_date_value_dict = {}
    origin_data = data_sets['data']
    if type(data_sets['data_sets']['resource']) is not list:
        sets_date_value_dict['date'], sets_date_value_dict['value'] = get_resource_datetime_and_value(
            origin_data, default_time
        )
        result_list.append(sets_date_value_dict)
        return result_list

    for sync_fhir_resource in data_sets['data_sets']['resource']:
        origin_data['resource'] = sync_fhir_resource
        sets_date_value_dict['date'], sets_date_value_dict['value'] = get_resource_datetime_and_value(
            origin_data, default_time
        )
        result_list.append(sets_date_value_dict.copy())
    return result_list


if __name__ == '__main__':
    import os

    os.chdir("../")

    from search_sets import get_patient_resources
    from search_sets import get_resource_datetime_and_value
    from feature_table import feature_table

    features__table = feature_table
    patient__id = "test-03121002"
    feature__table = features__table.get_model_feature_dict('diabetes')
    default_time = datetime.datetime.now()

    print(model_feature_search_with_patient_id(patient__id, feature__table, default_time))

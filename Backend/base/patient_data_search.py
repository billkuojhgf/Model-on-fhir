import datetime
from base.search_sets import get_patient_resources
from base.search_sets import get_patient_resources_data_set
from base.search_sets import get_resource_datetime_and_value
from base.search_sets import get_datetime_value_with_func


def model_feature_search_with_patient_id(patient_id: str,
                                         table: dict,
                                         default_time: str = None,
                                         data_alive_time: str = None) -> dict:
    """
    This function will return the result of model feature search with patient id. Different from smart search, this
    function will return the single result in dictionary type with the search_type defined in feature table.
    :param patient_id:
    :param table:
    :param default_time:
    :param data_alive_time:
    :return: return date and value in dictionary type
    e.g.: {'date': "2020-12-13", 'value': 87}
    """
    result_dict = smart_model_feature_search_with_patient_id(patient_id, table, default_time, data_alive_time)

    for key in result_dict:
        """
        get_datetime_value_with_func will return date and value in dictionary type
        return e.g.: {'date': "2020-12-13", 'value': 87}
        """
        result_dict[key] = get_datetime_value_with_func(result_dict[key], table[key])

    return result_dict


def smart_model_feature_search_with_patient_id(patient_id: str,
                                               table: dict,
                                               default_time: str = None,
                                               data_alive_time: str = None) -> dict:
    if default_time is None:
        default_time = datetime.datetime.now()

    # First is to get all patient resources from FHIR server.
    data = dict()
    for key in table:
        data[key] = dict()
        data[key] = get_patient_resources_data_set(patient_id, table[key], default_time, data_alive_time)

    # Next is to extract the data in data sets.
    result_dict = dict()
    for data_key in data:
        result_dict[data_key] = dict()
        result_dict[data_key] = extract_data_in_data_sets(data[data_key], default_time)

    # smart_model_feature_search_with_patient_id will return datetime and value in dictionary type
    # e.g.:{
    #       "diastolic blood pressure": {
    #          "date": ["2020-12-13", "2020-12-14", "2020-12-15"],
    #         "value": [87, 87, 87]
    #      },...
    #   }
    return result_dict


def extract_data_in_data_sets(data_sets, default_time) -> dict:
    """
    This function will extract the data in data_sets and return a dictionary
    :param data_sets:
    :param default_time:
    :return: All features value and date in dictionary type
    e.g.:{
        "diastolic blood pressure": {
            "date": ["2020-12-13", "2020-12-14", "2020-12-15"],
            "value": [87, 87, 87]
        },...
    }
    """
    result_list = {"date": [], "value": []}
    origin_data = data_sets.copy()
    if type(data_sets['resource']) is not list:
        temp_date, temp_value = get_resource_datetime_and_value(
            origin_data, default_time
        )

        result_list['date'].append(temp_date)
        result_list['value'].append(temp_value)
        return result_list

    for sync_fhir_resource in data_sets['resource']:
        origin_data['resource'] = sync_fhir_resource
        temp_date, temp_value = get_resource_datetime_and_value(
            origin_data, default_time
        )
        result_list['date'].append(temp_date)
        result_list['value'].append(temp_value)
    return result_list


if __name__ == '__main__':
    import os

    os.chdir("../")

    from search_sets import get_patient_resources
    from search_sets import get_resource_datetime_and_value
    from feature_table import feature_table

    features__table = feature_table
    patient__id = "test-03121002"
    feature__table = features__table.get_model_feature_dict('pima_diabetes')
    default_time = datetime.datetime.now()

    print(model_feature_search_with_patient_id(patient__id, feature__table, default_time))

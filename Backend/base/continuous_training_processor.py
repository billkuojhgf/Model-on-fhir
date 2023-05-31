import numpy as np
import pandas as pd
from datetime import date, datetime
from requests.exceptions import HTTPError

from base.exceptions import ThresholdNoneError
from base.exceptions import VariableNoneError
from base.object_store import bulk_server
from base.object_store import feature_table
from base.object_store import model_feature_table
from base.object_store import training_feature_table
from base.object_store import training_model_feature_table
from base.object_store import training_sets_table
from base.route_converter import get_by_path
from base.patient_data_search import extract_data_in_data_sets
from base.search_sets import get_datetime_value_with_func
from base.model_input_transformer import transformer
from base.lib import transform_to_correct_type


# First, we need to check what features are those resources belong to.
def separate_patients(resource: dict) -> dict:
    """
    While retrieving the data from the bulk server, we need to separate the data by patient.
    :param resource: dictionary. Keys are the resource type, and values are the list of resources.
    :return: dictionary. Keys are the patient id, and values are the list of resources.
    """
    return_data = {}
    for resources in resource["Patient"]:
        return_data[resources["id"]] = [resources]

    for resource_type, resources in resource.items():
        if resource_type == "Patient":
            continue
        for resource in resources:
            try:
                if resource["subject"]["id"] in return_data:
                    return_data[resource["subject"]["id"]].append(resource)
            except KeyError:
                continue

    return return_data


def allocate_feature_resources(resources, code_dict) -> dict:
    """
    Allocate the resources by the feature table configurations.

    :return:
    """
    return_data = {}

    # Iterate all the patients.
    for patient_id, resources in resources.items():
        patient_separated_data = {}
        for resource in resources:
            try:
                codes = code_dict[resource["resourceType"]]
            except KeyError:
                continue

            for feature_name, code_list in codes.items():
                if feature_name not in patient_separated_data:
                    patient_separated_data[feature_name] = []

                if resource["resourceType"] == "Patient":
                    patient_separated_data[feature_name].append(resource)
                    continue

                for code in code_list:
                    if get_by_path(resource, code) is not None:
                        patient_separated_data[feature_name].append(resource)
                        break

        for patient_separated_data_key, patient_separated_data_value in patient_separated_data.items():
            if len(patient_separated_data_value) == 0:
                # 當無資料時，補個None
                patient_separated_data[patient_separated_data_key].append(None)

        return_data[patient_id] = patient_separated_data

    return return_data


def combine_training_and_predicting_feature_table(model_name: str):
    """
    Combine the training and predicting feature table.
    :param training_feature_table:
    :param feature_table:
    :return:
    """
    # Combine the feature table of training and predicting.
    training_feature_code_dict = get_feature_code_dict(training_feature_table, model_name)
    feature_code_dict = get_feature_code_dict(feature_table, model_name)
    code_dict = {}
    for key in set(list(feature_code_dict.keys()) + list(training_feature_code_dict.keys())):
        code_dict[key] = feature_code_dict.get(key, {})
        code_dict[key].update(training_feature_code_dict.get(key, {}))

    return code_dict


def get_feature_code_dict(table, model_name) -> dict:
    """
    Get the feature code dictionary for the model.
    :param model_name:
    :return: {resource_type: {features: [{"code": str, "system": str or None}]}}
    """
    feature_code_dict = {}

    for feature_name, feature_dict in table.get_model_feature_dict(model_name).items():
        # For the features, we need to store the code for each feature.
        # {"Observation": {"Glucose": [route of codes...]} ... }
        resource_type = feature_dict["type_of_data"].capitalize()
        if resource_type not in feature_code_dict:
            feature_code_dict[resource_type] = {}

        temp_code_system_list = []
        for code_system in feature_dict["code"].split(","):
            temp_code_system_dict = {}

            if "|" in code_system:
                feature_system, feature_code = code_system.split("|")
                temp_code_system_dict["code"] = feature_code
                temp_code_system_dict["system"] = feature_system
            else:
                temp_code_system_dict["code"] = code_system

            temp_code_system_list.append(["code", "coding", temp_code_system_dict])

        feature_code_dict[resource_type][feature_name] = temp_code_system_list

    return feature_code_dict


def extract_value_and_datetime(resources: dict, table) -> dict:
    """
    Extract the value and datetime from the resources.

    :param resources: dictionary. Keys are the patient id, and values are the list of resources.
    :return: dictionary. Keys are the patient id, and values are the list of resources.
    """
    return_data = {}
    for patient_id, resources in resources.items():
        patient_separated_data = {}
        for feature_name, resources in resources.items():
            temp_data = {"resource": resources, "type": table[feature_name]["type_of_data"]}
            patient_separated_data[feature_name] = extract_data_in_data_sets(temp_data, table[feature_name])

        return_data[patient_id] = patient_separated_data

    return return_data


def filter_data_in_data_sets(data_sets: dict, filter_list):
    """
    Filter the data in the data sets.
    :param data_sets: dict, {"datetime": [], "value": []}
    :param filter_list:
    :return:
    """

    return_dict = {}
    # Prepare the thresholds

    # First, convert data_sets from dictionary to list to make it easier to filter.
    # Expected: [({date1}, {value1}), ...]

    data_sets_list = list(zip(data_sets["date"], data_sets["value"]))

    # Some exceptions for Patient data. Still need some clever way for Patient data exceptions.
    if len(data_sets_list) == 1:
        try:
            if datetime.fromisoformat(data_sets_list[0][0]) == datetime.fromordinal(date.today().toordinal()):
                return_dict["date"], return_dict["value"] = zip(*data_sets_list)
                return_dict["date"] = list(return_dict["date"])
                return_dict["value"] = list(return_dict["value"])
                return return_dict
        except TypeError:
            pass

    # Iterate the filter list.
    return_dict["date"] = []
    return_dict["value"] = []
    for date_value_set in data_sets_list:
        filter_list_validate = []
        for obj in filter_list:
            if obj.type == "date":
                validated_data = transform_to_correct_type(date_value_set[0], "date")
            elif obj.type == "value":
                validated_data = transform_to_correct_type(date_value_set[1])
            else:
                raise ValueError("The type of filter is not supported.")

            try:
                validate = obj.validate(validated_data)
            except ThresholdNoneError:
                validate = True
            except VariableNoneError:
                validate = False
            filter_list_validate.append(validate)
            if not validate:
                break

        if all(filter_list_validate):
            return_dict["date"].append(date_value_set[0])
            return_dict["value"].append(date_value_set[1])

    return return_dict


def extract_value(value_and_datetime_of_patients_after_filter) -> dict:
    return_data = {}
    for patient_id, value_and_datetime_of_patient in value_and_datetime_of_patients_after_filter.items():
        feature_value = {}
        for feature_name, value_and_datetime_of_feature in value_and_datetime_of_patient.items():
            feature_value[feature_name] = value_and_datetime_of_feature["value"] if value_and_datetime_of_feature[
                "value"] else np.nan
        return_data[patient_id] = feature_value

    return return_data


def resources_filter(value_and_datetime_of_patients, feature_table, filter_list) -> dict:
    """
    Filter the resources by the filter list.
    :param value_and_datetime_of_patients:
    :param filter_list:
    :return:
    """
    return_data = {}
    for patient_id, value_and_datetime_of_patient in value_and_datetime_of_patients.items():
        patient_separated_data = {}
        # First is to get the datetime and value of the filtered features
        # filtered_features =
        value_and_datetime_for_threshold_feature = {}
        for obj in filter_list:
            threshold = str(obj.threshold)
            if threshold.startswith("[") and threshold.endswith("]"):
                # keep the value inside []
                threshold = threshold[1:-1]
                # get the datetime and value with search_type strategy defined in feature table
                # store the rest data
                value_and_datetime_threshold = value_and_datetime_of_patient.pop(threshold)
                value_and_datetime_for_threshold_feature[threshold] = value_and_datetime_threshold
                # get the value and datetime with the strategy defined in feature table
                threshold = get_datetime_value_with_func(
                    value_and_datetime_threshold, feature_table[threshold])
                threshold = threshold[obj.type]

                # update the threshold to the object
                obj.threshold = threshold

        for feature_name, value_and_datetime_of_features in value_and_datetime_of_patient.items():
            patient_separated_data[feature_name] = \
                filter_data_in_data_sets(value_and_datetime_of_features, filter_list)

        patient_separated_data = patient_separated_data | value_and_datetime_for_threshold_feature

        return_data[patient_id] = patient_separated_data

    # get the value and datetime with the strategy defined in feature table
    for patient_id, value_and_datetime_of_patient in return_data.items():
        for feature_name, value_and_datetime_of_features in value_and_datetime_of_patient.items():
            return_data[patient_id][feature_name] = \
                get_datetime_value_with_func(value_and_datetime_of_features, feature_table[feature_name])

    return return_data


def null_value_stategy(df: pd.DataFrame, null_value_strategy: dict) -> pd.DataFrame:
    """
    Fill the null value in the dataframe with the strategy defined in the null_value_strategy.
    :param df:
    :param null_value_strategy:
    :return:
    """
    # Drop the rows with too many null values
    return_df = df
    drop_prefix = null_value_strategy["drop"]["prefix"]
    drop_threshold = int(null_value_strategy["drop"]["threshold"])
    if drop_prefix == "ge":
        return_df = return_df[return_df.isnull().sum(axis=1) < drop_threshold]
    elif drop_prefix == "gt":
        return_df = return_df[return_df.isnull().sum(axis=1) <= drop_threshold]
    else:
        raise ValueError("The prefix of drop is not supported.")

    # Fill the null value with the strategy defined in the null_value_strategy
    del null_value_strategy["drop"]

    # Pop the default strategy, and be ready to fill the rest columns based on the config of the strategy.
    default_strategy = null_value_strategy.pop("default")
    for feature_name, strategy in null_value_strategy.items():
        if strategy == "mean":
            return_df[feature_name].fillna(return_df[feature_name].mean(), inplace=True, downcast="infer")
        elif strategy == "median":
            return_df[feature_name].fillna(return_df[feature_name].median(), inplace=True, downcast="infer")
        elif strategy == "mode":
            return_df[feature_name].fillna(return_df[feature_name].mode()[0], inplace=True, downcast="infer")
        elif type(transform_to_correct_type(strategy)) in [int, float]:
            return_df[feature_name].fillna(transform_to_correct_type(default_strategy), inplace=True, downcast="infer")
        else:
            raise ValueError("The type of null value strategy is not supported.")

    # Fill the rest columns with the default strategy
    if default_strategy == "mean":
        return_df.fillna(return_df.mean(), inplace=True, downcast="infer")
    elif default_strategy == "median":
        return_df.fillna(return_df.median(), inplace=True, downcast="infer")
    elif default_strategy == "mode":
        for feature_name in return_df.columns:
            return_df[feature_name].fillna(return_df[feature_name].mode()[0], inplace=True, downcast="infer")
    elif type(transform_to_correct_type(default_strategy)) in [int, float]:
        return_df.fillna(transform_to_correct_type(default_strategy), inplace=True, downcast="infer")
    else:
        raise ValueError("The type of null value strategy is not supported.")

    return return_df


def transform_data(
        model_feature_table,
        value_and_datetime_of_patients_after_filter,
        model_name
) -> dict:
    """
    Transform the data to the format that can be used in the model.
    :param model_feature_table:
    :param value_and_datetime_of_patients_after_filter:
    :param model_name:
    :return:
    """
    return_dict = {}

    for patient_id, value_and_datetime_of_patient in value_and_datetime_of_patients_after_filter.items():
        transformed_data_list = transformer(model_feature_table, value_and_datetime_of_patient, model_name)
        return_dict[patient_id] = transformed_data_list

    return return_dict


def merge_transformed_data(x_data_dict, y_data_dict) -> dict:
    """
    Merge the transformed data to the format that can be used in the model.
    :param args:
    :return:
    """
    return_dict = x_data_dict
    for patient_id, y_data in y_data_dict.items():
        if not all(y_data):
            del return_dict[patient_id]
        else:
            return_dict[patient_id] = return_dict[patient_id] + y_data

    return return_dict


def main_process(model_name):
    # # Add exception for error 404
    # try:
    #     bulk_server.content = "http://ming-desktop.ddns.net:8193/fhir/$export-poll-status?_jobId=c0816f00-576b-4e4a-9e51-18d358b41bd3"
    #     bulk_server.provision()
    # except HTTPError:
    #     print("Connection error. Trying to generate a new bulk request")
    #     bulk_server.content = None
    #     bulk_server.provision()
    #     print(bulk_server.content)
    #
    # ndj = bulk_server.iter_ndjson_dict()
    # code_dict = combine_training_and_predicting_feature_table(model_name)
    # data_with_separated_patient = separate_patients(ndj)
    # data_with_separated_patient = allocate_feature_resources(data_with_separated_patient, code_dict)
    #
    # # Extract the value and datetime from the resources.
    # predict_and_training_feature_tables = \
    #     feature_table.get_model_feature_dict(model_name) | training_feature_table.get_model_feature_dict(model_name)
    # value_and_datetime_of_patients = extract_value_and_datetime(
    #     data_with_separated_patient, predict_and_training_feature_tables)
    #
    # # Drop the resources that are not needed.
    # value_and_datetime_of_patients_after_filter = resources_filter(
    #     value_and_datetime_of_patients,
    #     predict_and_training_feature_tables,
    #     training_sets_table.get_training_set(model_name).data_filter
    # )
    #
    # # translate the value from the value_and_datetime_of_patients_after_filter
    # transformed_x_data_of_patients = transform_data(model_feature_table,
    #                                                 value_and_datetime_of_patients_after_filter,
    #                                                 model_name)
    # transformed_y_data_of_patients = transform_data(training_model_feature_table,
    #                                                 value_and_datetime_of_patients_after_filter,
    #                                                 model_name)
    #
    # transformed_training_data = merge_transformed_data(transformed_x_data_of_patients,
    #                                                    transformed_y_data_of_patients)
    #
    # # Time for some dataframe works
    # column = model_feature_table.get_model_feature_column(model_name) \
    #             + training_model_feature_table.get_model_feature_column(model_name)
    # df = pd.DataFrame.from_dict(transformed_training_data, orient="index")
    # df.columns = column
    # df.to_csv("test.csv")

    df = pd.read_csv("test.csv", index_col=0)
    df_new = null_value_stategy(df, training_sets_table.get_training_set(model_name).null_value_strategy)
    pass


if __name__ == "__main__":
    print("starting...")
    main_process("SPC")
    print("ending...")
    pass

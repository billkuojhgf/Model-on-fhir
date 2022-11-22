import operator
from base.model_feature_table import feature_table


def get_model_input(value, transfer):
    return True


def transformer(patient_data_dict: dict, model: str) -> list:
    """
    This function takes the transformation of patient data into model input. The function requires patient data with
    dictionary and returns the list of the data.
    :param patient_data_dict: value of patient data from client or FHIR server
    :param model: name of model
    :return: list that are ready for prediction. Sort features by index.
    """
    transform_style = feature_table.get_model_feature_dict(model_name=model)
    # First, transfer patient numeric data to model require format
    # getattr(operator, 'eq')(2, 3)
    model_data_dict = dict()
    formula_idle_job = []
    for name in patient_data_dict.keys():
        if name not in transform_style.keys():
            # the action can be changed while MoCab supports features in formula do transfer.
            continue

        if transform_style[name]['type'] == 'formula':
            formula_idle_job.append(name)
            continue

        model_data_dict[name] = get_model_input(patient_data_dict[name].value, transform_style[name])

    # At last, pack data into list.

    return []


if __name__ == "__main__":
    print(globals()["operator"]['eq'](2, 3))

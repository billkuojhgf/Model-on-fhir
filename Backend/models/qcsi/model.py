import mask
from typing import Dict
from mask import unit_type
from mask import mask_type


def predict(data: dict) -> int:
    """
    patient_data_dict is a dictionary that contains respiratory rate, o2 flow rate and spo2.
    The value of the keys are in dictionary type too, they are all in the same structure with date and value key-value.
    Date sometimes would be optional but the value must be required.

    The o2 flow rate key has two kinds of value, number of string.
    If the value of o2 flow rate is number, then it can be used without any further instructions.
    But if the value of o2 flow rate is string, it should be converted to the number by
    the method: mask_mart.treatment_mining(your_text_here), the method would return the number of the string.

    The goal of this function is to calculate the qCSI value with patient data that was given in patient_data_dict,
    and return the qCSI score.
    """

    flow_rate_value = data["o2_flow_rate"]['value']
    if type(flow_rate_value) == str:
        treatment_mining_result = \
            mask.mask_mart.treatment_mining(flow_rate_value)
        if treatment_mining_result is not None:
            # TODO: Convert FiO2 to Flow rate
            if treatment_mining_result['unit_type'] != unit_type[0]:
                data["o2_flow_rate"]["value"] = unit_conversion(treatment_mining_result)
            else:
                data["o2_flow_rate"]['value'] = treatment_mining_result['value']
        else:
            raise ValueError("The O2 flow rate string: \"{}\" cannot be identified \
            , please fill in the flow rate manually"
                             .format(flow_rate_value))
    # Convert the value into qCSI score format and calculate the score.
    return qcsi_model_result(data)


def qcsi_model_result(patient_data_dict) -> int:
    result = 0
    for key in patient_data_dict:
        try:
            result += {
                'respiratory_rate':
                    0 if patient_data_dict[key]['value'] <= 22
                    else 2 if patient_data_dict[key]['value'] >= 28
                    else 1,
                'spo2':
                    5 if patient_data_dict[key]['value'] <= 88
                    else 0 if patient_data_dict[key]['value'] > 92
                    else 2,
                'o2_flow_rate':
                    0 if patient_data_dict[key]['value'] <= 2
                    else 5 if patient_data_dict[key]['value'] >= 5
                    else 4
            }.get(key)
        # Handle the exception to the not exist keys.
        except TypeError:
            print("key '{}' is not using, continue anyway.".format(key))
            continue
    return result


def unit_conversion(treatment_mining_result: Dict) -> int or float:
    """
    treatment_mining_result: Dict, {'mask_name': , 'mask_type', 'value'}
    unit_type = ("o2_flow_rate", "fio2")
    mask_type = ("Simple Mask", "Nasal Cannula", "Non-rebreathing Mask", "Tracheal Mask", "V-Mask", "High Flow Mask")
    """
    converted_value = 0
    fio2_value = int(treatment_mining_result['value'])
    # TODO: 補齊轉換的單位數值
    if treatment_mining_result['mask_name'] == mask_type[0]:
        converted_value = (fio2_value - 5) / 5
    elif treatment_mining_result['mask_name'] == mask_type[1]:
        converted_value = (fio2_value - 20) / 4
    elif treatment_mining_result['mask_name'] == mask_type[2]:
        converted_value = 15
    elif treatment_mining_result['mask_name'] == mask_type[3]:
        converted_value = (fio2_value - 21) / 3
    else:
        raise KeyError("Mask Name Undefined, check mask.mask_type sets for more info.")
    return round(converted_value)


if __name__ == '__main__':
    mask.mask()
    patient_data = {
        "respiratory_rate": {
            "date": "2022-01-19T11:53",
            "value": 25
        },
        "o2_flow_rate": {
            "date": "2022-01-19T11:53",
            "value": "O2 nasal 3l/min use"
        },
        "fio2": "",
        "spo2": {
            "date": "2022-01-19T11:53",
            "value": 90
        }
    }
    print(predict(patient_data))

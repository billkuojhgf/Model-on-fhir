import operator
import re
from datetime import datetime

import numpy as np


def transform_to_correct_type(input_string: str, special_type="value"):
    special_types = ["value", "date"]
    if special_type not in special_types:
        raise ValueError(f"special_type must be one of {special_types}")

    if special_type == 'date':
        return datetime_handler(input_string)

    input_string = str(input_string)
    mapping_dict = {
        "true": True,
        "false": False,
        "nan": np.nan,
        "none": None
    }

    if input_string.lower() in mapping_dict:
        return mapping_dict[input_string.lower()]

    try:
        output = int(input_string)
    except ValueError:
        try:
            output = float(input_string)
        except ValueError:
            output = input_string

    return output


def datetime_handler(date_string: str or datetime):
    """
    Handle the datetime string to datetime object.
    """
    if type(date_string) == datetime:
        return date_string

    if date_string == "" or date_string is None:
        return None

    datetime_format = [
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%SZ"
    ]
    try:
        return datetime.fromisoformat(date_string)
    except ValueError:
        for fmt in datetime_format:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue

    raise ValueError("The datetime string is not in correct format.")


class TimeObject:
    def __init__(self, data_alive_time):
        self._years = 0
        self._months = 0
        self._days = 0
        self._hours = 0
        self._minutes = 0
        self._seconds = 0
        self.__set_data_alive_time(data_alive_time)

    def __set_data_alive_time(self, data_alive_time):
        datetime_prog = re.compile(
            r"[0-9]{4}-(0[0-9]|1[12])-([12][0-9]|3[01]|0[0-9])T(20|21|22|23|[0-1]\d):[0-5]\d:[0-5]\d")
        date_prog = re.compile(r"[0-9]{4}-(0[0-9]|1[12])-([12][0-9]|3[01]|0[0-9])")
        if datetime_prog.search(data_alive_time):
            date, time = data_alive_time.split(
                'T')[0], data_alive_time.split('T')[1]
            self._years = int(date.split('-')[0])
            self._months = int(date.split('-')[1])
            self._days = int(date.split('-')[2])
            self._hours = int(time.split(':')[0])
            self._minutes = int(time.split(':')[1])
            self._seconds = int(time.split(':')[2])
        elif date_prog.search(data_alive_time):
            self._years = int(data_alive_time.split('-')[0])
            self._months = int(data_alive_time.split('-')[1])
            self._days = int(data_alive_time.split('-')[2])
        else:
            raise ValueError(
                "The Time Format is incorrect, " + data_alive_time)

    def get_years(self):
        return self._years

    def get_months(self):
        return self._months

    def get_days(self):
        return self._days

    def get_hours(self):
        return self._hours

    def get_minutes(self):
        return self._minutes

    def get_seconds(self):
        return self._seconds

    def return_datetime(self):
        return datetime(self._years, self._months, self._days, self._hours, self._minutes, self._seconds)


class BaseVariable:
    def __init__(self, feature, var_type):
        """
        Base object of all variables

        :param feature: name of feature
        :param var_type: type of variable, e.g. numeric, category, and formulate.
        """
        self.feature = feature
        self.type = var_type

    def get_value(self):
        pass


class Operation:

    # TODO: 原先的variable可以為None, 但為什麼？
    def __init__(self, variable: BaseVariable, threshold, prefix: str = "eq"):
        # Handle nan situation
        if threshold == "nan":
            threshold = np.nan
            if prefix == "eq":
                prefix = "is_"
            elif prefix == "ne":
                prefix = "is_not"
            else:
                raise ValueError(f"prefix {prefix} is not valid for nan threshold.")

        self.variable = variable
        self.prefix = prefix
        self.threshold = threshold

    def validate(self):
        try:
            # TODO: 要想一下get_value 如果為nan時會不會有什麼Error
            thres = self.threshold
            if issubclass(type(thres), BaseVariable):
                thres = self.threshold.get_value()

            var = self.variable.get_value()

            return getattr(operator, self.prefix)(transform_to_correct_type(var), transform_to_correct_type(thres))
        except KeyError:
            raise AttributeError(f"{self.prefix} is not a valid operator.")

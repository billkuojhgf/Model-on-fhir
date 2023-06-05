import csv
import operator
import re

import numpy as np

from datetime import datetime
from base.lib import TimeObject, BaseVariable, transform_to_correct_type
from base.exceptions import VariableNoneError, ThresholdNoneError


class _TrainingSet:

    def __init__(self,
                 data_filter: list,
                 duration: TimeObject,
                 null_value_strategy: dict,
                 training_config: dict):
        self.data_filter = data_filter
        self.duration = duration
        self.null_value_strategy = null_value_strategy
        self.training_config = training_config


class FilterOperation:

    # TODO: 原先的variable可以為None, 但為什麼？
    def __init__(self, threshold, prefix: str = "eq", type: str = "value"):
        # Doesn't support nan threshold.
        # Reason: nan is not a valid filter while training. (Or maybe is?)
        self.prefix = prefix
        self.type = type
        self._threshold = threshold

    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self, value):
        if value == "nan":
            raise ValueError(f"nan is not a valid threshold.")
        else:
            self._threshold = value

    def validate(self, variable):
        if type(variable) == BaseVariable:
            var = variable.get_value()
        else:
            var = variable

        if type(self._threshold) == BaseVariable:
            thres = self._threshold.get_value()
        else:
            thres = self._threshold

        # Transfer to correct type
        thres = transform_to_correct_type(thres, self.type)
        var = transform_to_correct_type(var, self.type)

        # 目前想下來，當比較單位為時間，則threshold必須為datetime，否則回傳錯誤
        if thres is None:
            raise ThresholdNoneError(f"Threshold is None on {self.type} type.")

        if var is None:
            raise VariableNoneError(f"Variable is None on {self.type} type.")

        try:
            return getattr(operator, self.prefix)(var, thres)
        except KeyError:
            raise AttributeError(f"{self.prefix} is not a valid operator.")
        except TypeError as e:
            raise e


class _TrainingSetTable:

    def __init__(self, table_position="./config/continuous_training/training_sets.csv"):
        self.table = self.__create_table(table_position)

    def __create_table(self, table_position) -> dict:
        with open(table_position, newline='') as training_sets_table:
            return_dict = {}
            rows = csv.DictReader(training_sets_table)

            for row in rows:
                special_columns = ["models", "filter", "duration", "null_value_strategy", "threshold"]
                data_filter = self.data_filter_handler(row["filter"])
                duration = TimeObject(row["duration"])
                null_value_strategy = self.null_value_strategy_handler(row["null_value_strategy"])
                training_configs = dict()

                if row['threshold'] is None:
                    training_configs['threshold'] = 0.5
                else:
                    training_configs['threshold'] = float(row['threshold'])

                for key, value in row.items():
                    if key not in special_columns:
                        training_configs[key] = value

                return_dict[row["models"]] = \
                    _TrainingSet(data_filter, duration, null_value_strategy, training_configs)

            return return_dict

    @staticmethod
    def data_filter_handler(param) -> list:
        regex = re.compile(r"(\((date|value)\))?((eq|ne|lt|le|gt|ge)\|)?((\[\w+])|(\S+))")
        return_list = []
        for sub_param in param.split("&"):
            sub_param_regex = regex.match(sub_param)
            typing = "value"
            prefix = "eq"

            if sub_param_regex:
                if sub_param_regex.group(2) is not None:
                    typing = sub_param_regex.group(2)

                if sub_param_regex.group(4) is not None:
                    prefix = sub_param_regex.group(4)

                if sub_param_regex.group(6) is not None:
                    threshold = sub_param_regex.group(6)
                elif sub_param_regex.group(7) is not None:
                    threshold = sub_param_regex.group(7)
                else:
                    raise ValueError(f"data_filter format error: Must have threshold. Error: {sub_param}")
            else:
                raise ValueError("data_filter format error")

            return_list.append(
                FilterOperation(threshold=threshold, prefix=prefix, type=typing)
            )

        return return_list

    @staticmethod
    def null_value_strategy_handler(param) -> dict:
        return_dict = {}

        # Handle drop strategy first
        drop_param = param.split("&")[0]
        drop_regex = re.compile(r"\(drop\)((gt|ge)\|)?(\d+)")

        # Error handling
        if not drop_regex.match(drop_param):
            raise ValueError(f"null_value_strategy has a wrong structure in drop: '{drop_param}'")

        prefix = "lt"
        if drop_regex.match(drop_param).group(2) is not None:
            prefix = drop_regex.match(drop_param).group(2)
        threshold = drop_regex.match(drop_param).group(3)
        return_dict["drop"] = {
            "prefix": prefix,
            "threshold": threshold
        }

        # Handle fillna strategy
        fillna_param = "&".join(param.split("&")[1:])
        fillna_regex = re.compile(r"(\((median|mean|mode)\)|([\.\w]+))\|?(\[(\w+)])?")
        for sub_param in fillna_param.split("&"):
            method = None
            column = "default"

            # Error handling while wrong structure
            if not fillna_regex.match(sub_param):
                raise ValueError(f"null_value_strategy has a wrong structure in fillna: '{sub_param}'")

            if fillna_regex.match(sub_param).group(2) is not None:
                method = fillna_regex.match(sub_param).group(2)

            if fillna_regex.match(sub_param).group(3) is not None:
                if method is not None:
                    raise ValueError(f"null_value_strategy has a wrong structure in fillna: '{sub_param}'")
                method = transform_to_correct_type(fillna_regex.match(sub_param).group(3))

            if fillna_regex.match(sub_param).group(5) is not None:
                column = fillna_regex.match(sub_param).group(5)

            # Error handling while duplicated
            if column in return_dict:
                if column == "default":
                    raise ValueError(f"null_value_strategy has a duplicated default fillNA strategy: '{fillna_param}'")
                raise ValueError(f"null_value_strategy has a duplicated column: '{sub_param}'")

            return_dict[column] = method

        return return_dict

    def get_training_set(self, name: str) -> _TrainingSet:
        return self.table[name]

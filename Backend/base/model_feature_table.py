import csv
import re

"""
    data structure of _ModelFeature :
        {
            model name: {
                feature: {
                    "type": category or value,
                    "case": [{
                        "prefix": prefix, prefix in ModelFeature or None
                        "condition": value, int or float or str, time would probably be needed(any situation?),
                        "category": category
                    }]
                }
            }
        }
"""
prefix_list = [
    "eq",
    "ne",
    "gt",
    "lt",
    "ge",
    "lt",
    "ge",
    "le"
]

type_list = [
    "category",
    "value"
]


class _ModelFeature:
    def __init__(self, model_feature_table_position):
        self.table = self.__create_table(model_feature_table_position)

    @classmethod
    def __create_table(cls, model_feature_table_position):
        # two types of case_of_category, "regex with prefix" or "regex without prefix".
        regex_with_prefix = re.compile(r"(.*?) ?= ?([a-zA-Z]{2})\|(.*)")
        regex_without_prefix = re.compile(r"(.*?) ?= ?(.*)")
        table = {}

        with open(model_feature_table_position, newline='') as model_feature_table:
            rows = csv.DictReader(model_feature_table)
            for row in rows:
                # TODO: simple the code, combine these checks into an exception_check() function.
                result_regex_with_prefix = regex_with_prefix.search(row["case_of_category"])
                result_regex_without_prefix = regex_without_prefix.search(row['case_of_category'])

                if str(row['type']).lower() not in type_list:
                    raise AttributeError(f"{row['type']} is not a legal type, expect {type_list}.")

                # 新建以model 為Key 的Dictionary
                if row['model'] not in table:
                    table[row['model']] = {}
                # 在model 中新增該feature 的Dictionary
                if row['feature'] not in table[row['model']]:
                    table[row['model']][row['feature']] = {}

                # 撰寫該feature 的type
                table[row['model']][row['feature']]["type"] = str(row['type']).lower()

                table[row['model']][row['feature']]["index"] = int(row['index']) if row['index'] != "" else None

                if str(row['type']).lower() == "category":
                    # Check case_of_category regex while type is in category
                    if not result_regex_with_prefix:
                        if not result_regex_without_prefix:
                            raise AttributeError(f"{row['case_of_category']} does not match the format.")

                    if "case" not in table[row['model']][row['feature']]:
                        table[row['model']][row['feature']]["case"] = list()

                    temp = {}
                    if result_regex_with_prefix:
                        if result_regex_with_prefix.group(2) not in prefix_list:
                            raise AttributeError(f"{row['case_of_category']} has invalid prefix.")
                        temp['category'] = transform_to_correct_type(result_regex_with_prefix.group(1))
                        temp['prefix'] = result_regex_with_prefix.group(2)
                        temp['condition'] = transform_to_correct_type(result_regex_with_prefix.group(3))
                    elif result_regex_without_prefix:
                        temp['category'] = transform_to_correct_type(result_regex_without_prefix.group(1))
                        temp['prefix'] = "eq"
                        temp['condition'] = transform_to_correct_type(result_regex_without_prefix.group(2))

                    table[row['model']][row['feature']]["case"].append(temp)

        return table


    def get_model_feature_dict(self, model_name):
        # TODO: table_obj = DefaultMunch.fromDict(table.table), change table into table object
        if model_name not in self.table:
            raise KeyError("Model is not exist in the feature table.")

        return self.table[model_name]


def transform_to_correct_type(input_string: str):
    if input_string.lower() == 'true':
        return True
    elif input_string.lower() == 'false':
        return False

    try:
        output = int(input_string)
    except ValueError:
        try:
            output = float(input_string)
        except ValueError:
            output = input_string

    return output

if __name__ != "__main__":
    feature_table = _ModelFeature("./config/ModelFeature.csv")

if __name__ == "__main__":
    import json

    model_feature_table = _ModelFeature("../config/ModelFeature.csv")
    print(json.dumps(model_feature_table.get_model_feature_dict("CHARM"), sort_keys=True, indent=4))

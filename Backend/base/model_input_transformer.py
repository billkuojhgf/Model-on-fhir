from base.object_store import model_feature_table


def transformer(data: dict, model_name):
    real_dict = model_feature_table.get_model_feature_dict(model_name)
    for k, v in data.items():
        try:
            real_dict["observer"].update_value(k, v["value"])
        except TypeError:
            continue

    return_list = []

    for element in real_dict["index"]:
        has_value = False
        for variable in element:
            try:
                if variable.get_value() is not None:
                    return_list.append(variable.get_value())
                    has_value = True
                    break
            except TypeError:
                continue
        # 所有Variable
        if not has_value:
            return_list.append(None)
            # TODO: add maybe an Nonetype of Nan to the list if there's no value in the variable

    return return_list


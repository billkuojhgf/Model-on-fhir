import importlib

from mocab_models import *
from base.model_input_transformer import transformer
from base.object_store import feature_table

table = feature_table


def verify_data(patient_data_dict, api):
    # MUST HAVE: 1. Keys with each feature. 2. Value with Dict type and has Key with the name "value".
    try:
        validation_table = table.get_model_feature_dict(api)
    except KeyError:
        raise KeyError("{} Model is not in the table".format(api))

    for key in validation_table.keys():
        if key not in patient_data_dict.keys():
            raise KeyError("{} was not given".format(key))

        if "value" not in patient_data_dict[key].keys():
            raise KeyError("{}'s value has no 'value' key.".format(key))


def return_model_result(patient_data_dict, api):
    """
        Function return_model_result會對 model執行 predict的動作，回傳 model的結果
        2022-10-10 新增一個新的動作：在丟入Model之前，會先將資料根據ModelFeature Table轉譯成model prefer的category
        TODO: 把return_model_result獨立成一個新的檔案，需要解決的技術難點: globals()[api]
    """

    # transfer patient data into model preferred input
    patient_data_list = transformer(patient_data_dict, api)
    model_results = globals()[api].predict(patient_data_list)
    return model_results


def import_model():
    # TODO: Need to figure out what actions does this function done, and optimize it.
    # get a handle on the module
    mdl = importlib.import_module('mocab_models')

    # is there an __all__?  if so respect it
    if "__all__" in mdl.__dict__:
        names = mdl.__dict__["__all__"]
    else:
        # otherwise we import all names that don't begin with _
        names = [x for x in mdl.__dict__ if not x.startswith("_")]

    # now drag them in
    globals().update({k: getattr(mdl, k) for k in names})


import_model()

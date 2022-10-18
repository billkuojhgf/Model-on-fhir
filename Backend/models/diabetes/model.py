import joblib


def predict(data: dict):
    # @data comes from two places, one is from diabetes_predict(), the other is from flask(not sure where yet).
    # data allows two kind of value set, one is dictionary(the value returned from get_resources()),
    #   another is value(the value comes from frontend)
    # Put all the values into temp and get ready to predict
    x = list()
    # fixed variable: pregnancies=6, skinthickness=35, diabetespedigreefunction=0.627
    # controlled variable: glucose, diastolic blood pressure, insulin, height, weight, age

    # TODO: get_age要重做，想一個好的辦法來處理這種例外情節
    temp = [
        6,
        data['glucose']['value'],
        data['diastolic_blood_pressure']['value'],
        35,
        data['insulin']['value'],
        bmi(data['height']['value'], data['weight']['value']),
        0.627,
        data['age']['value']
    ]
    loaded_model = joblib.load("./models/diabetes/finalized_model.sav")
    x.append(temp)
    result = loaded_model.predict_proba(x)
    # result = [no's probability, yes's probability]
    # return negative's probability
    return result[:, 1][0]


def bmi(height, weight):
    # weight(unit: kilogram)/ height(unit: meter)/ height(unit: meter)
    # weight = {
    #     'kg': weight_resource.valueQuantity.value,
    #     'g': weight_resource.valueQuantity.value / 1000,
    #     '[lb_av]': weight_resource.valueQuantity.value * 0.45359237
    # }.get(weight_resource.valueQuantity.unit, 0)
    # height = {
    #     'cm': height_resource.valueQuantity.value / 100,
    #     '[in_i]': height_resource.valueQuantity.value * 0.0254,
    # }.get(height_resource.valueQuantity.unit, 0)

    return float(weight) / float(height) / float(height)

import joblib


def predict(data: dict):
    """

    :param data:
            sea: Category. Whether the patient has contacted seawater or raw seafood, 0 or 1.
            wbc: Value. White Blood Cell. Normally between 4000-11000/mm3.
            crp: Value. C-Reactive Protein. Normally under 0.8mg/dL
            seg: Value. Segment. Normally between 40-70%
            band: Value. Banded white blood cell. Normally between 0-0.5%

    :return: float, Model Score
    """
    x = list()
    temp = [
        data['sea']['value'],
        data['wbc']['value'],
        data['crp']['value'],
        data['seg']['value'],
        data['band']['value']
    ]
    loaded_model = joblib.load("./LR_model_ZheYu_5fea")
    x.append(temp)
    result = loaded_model.predict_proba(x)
    return result[:, 1][0]


if __name__ == "__main__":
    patient_data = {
        "sea": {
            "value": 1
        },
        "wbc": {
            "value": 12200
        },
        "crp": {
            "value": 164.06
        },
        "seg": {
            "value": 83.1
        },
        "band": {
            "value": 0
        }
    }
    print(predict(patient_data))

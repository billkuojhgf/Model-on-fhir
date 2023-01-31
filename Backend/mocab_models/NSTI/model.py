import joblib


def predict(data: list):
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
    temp = data
    # Fixme: 路徑問題，待解決
    loaded_model = joblib.load("./mocab_models/NSTI/LR_model_NSTI_5fea")
    x.append(temp)
    result = loaded_model.predict_proba(x)
    return result[:, 1][0]


if __name__ == "__main__":
    patient_data = [1, 12900, 162.2, 86.6, 0]
    print(predict(patient_data))

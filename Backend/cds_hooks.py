import os
import base.cds_hooks_work as cds
from dotenv import load_dotenv
from app import return_model_result
from config import configObject as config
from base.patient_data_search import model_feature_search_with_patient_id
from base.feature_table import feature_table
from fhirpy.base.exceptions import ResourceNotFound
from mocab_models import *

load_dotenv()
cds_app = cds.App()


@cds_app.patient_view("MoCab-CDS-Service", "The patient greeting service greets a patient!", title="Patient Greeter")
def greeting(r: cds.PatientViewRequest, response: cds.Response):
    # TODO: authorize whether the server's url is real or not
    try:
        config["fhir_server"]["FHIR_SERVER_URL"] = r.fhirServer
    except Exception as e:
        print(e)
    # Add some if-else statement of models' using situation.
    for model_name in feature_table.get_exist_model_name():
        """
            1. 首先是要確認病患ID在資料庫中的資料集是否足夠，所以這時候會去試探Server看是否有數據
            2. 確認有資料後，就會將數據丟入Model中進行預測
            3. 預測完成後，根據Model Score判斷應該要回傳info card 或是 warning card (TODO: 需要一個表格去填寫何時使用warning card)
            4. 回傳Warning Card
        """
        try:
            patient_data_dictionary = model_feature_search_with_patient_id(r.context.patientId,
                                                                           feature_table.get_model_feature_dict(
                                                                               model_name))
        except (ResourceNotFound, KeyError) as e:
            continue

        try:
            patient_data_dictionary["predict_value"] = return_model_result(patient_data_dictionary, model_name)
        except KeyError as e:
            continue

        # TODO: 應該要有個表來表示正常數值的Range.
        if patient_data_dictionary['predict_value'] > 3:
            card = cds.Card.critical(f"Patient {r.context.patientId} has a high risk of \"{model_name}\".\n",
                                     cds.Source(label="MoCab CDS Service",
                                                url="https://www.mo-cab.dev",
                                                icon="https://i.imgur.com/sFUFOyO.png"),
                                     suggestions=[cds.Suggestion(label="Suggestions", isRecommended=True)],
                                     detail=f"On a high risk {model_name}, Model Score: {patient_data_dictionary['predict_value']}\nMore detail...")
            card.add_link(cds.Link.smart("MoCab-App",
                                         "http://localhost:5000/launch"))
        elif patient_data_dictionary['predict_value'] > 0.8:
            card = cds.Card.warning(f"Patient {r.context.patientId} has a warning of \"{model_name}\".\n",
                                    cds.Source(label="MoCab CDS Service",
                                               url="https://www.mo-cab.dev",
                                               icon="https://i.imgur.com/sFUFOyO.png"),
                                    suggestions=[cds.Suggestion(label="Suggestions")],
                                    detail=f"On a warning of {model_name}, Model Score: {patient_data_dictionary['predict_value']}\nMore detail...")
            card.add_link(cds.Link.smart("MoCab-App",
                                         "http://localhost:5000/launch"))
        else:
            card = cds.Card.info(f"Patient {r.context.patientId} looks fine on \"{model_name}\".\n",
                                 cds.Source(label="MoCab CDS Service",
                                            url="https://www.mo-cab.dev",
                                            icon="https://i.imgur.com/sFUFOyO.png"),
                                 suggestions=[cds.Suggestion(label="Suggestions")],
                                 detail=f"Looks fine on {model_name}, Model Score: {patient_data_dictionary['predict_value']}\nMore detail...")

            card.add_link(cds.Link.smart("MoCab-App",
                                         "http://localhost:5000/launch"))
        response.add_card(card)
    response.httpStatusCode = 200


def generate_cds_card() -> cds.Card:  # Model generate card.
    pass


if __name__ == '__main__':
    debug = os.environ.get('DEBUG', True)
    port = os.environ.get("PORT", 5001)
    cds_app.serve(host="0.0.0.0", debug=debug, port=port)

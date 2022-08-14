import cds_hooks_work as cds
import os

app = cds.App()


@app.patient_view("MoCab-CDS-Service", "The patient greeting service greets a patient!", title="Patient Greeter")
def greeting(r: cds.PatientViewRequest, response: cds.Response):
    # card = cds.Card.info("hello world!", cds.Source("demo_service"))
    card = cds.Card.warning("Patient {} is on the high risk of {} score".format("test-03121002", "qCSI")
                            , cds.Source(label="MoCab Website", url="https://www.mo-cab.dev", icon="https://i.imgur.com/sFUFOyO.png"))
    # card.add_link(cds.Link.absolute("cds-hooks-work", "https://mings.dev"))
    card.add_link(cds.Link.smart("MoCab-SMART", "https://mings.dev"))
    response.add_card(card)
    response.httpStatusCode = 200


if __name__ == '__main__':
    debug = os.environ.get('DEBUG', True)
    port = os.environ.get("PORT", 5001)
    app.serve(host="0.0.0.0", debug=debug, port=port)

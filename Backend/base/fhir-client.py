from fhirclient import client
import fhirclient.models.patient as p
settings = {
    'app_id': 'my_web_app',
    'api_base': 'http://localhost:8090/fhir',
    "authorize_url": "http://localhost:8091/auth"
}
smart = client.FHIRClient(settings=settings)

if __name__ == "__main__":
    patient = p.Patient.read("test-03121002", smart.server)

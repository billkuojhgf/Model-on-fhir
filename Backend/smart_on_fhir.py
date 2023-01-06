from app import mocab_app
from fhirclient.client import FHIRClient
from fhirclient.server import FHIRServer
from flask import request, redirect

smart_serverObj: FHIRServer
smart_clientObj: FHIRClient


@mocab_app.route("/launch", methods=['GET'])
def smart_launch():
    # TODO: Change redirect_uri
    settings = {
        'app_id': 'mocab_app',
        'api_base': request.values.get("iss"),
        'redirect_uri': "http://localhost:5000/fhir-app",
        'scope': " ".join(["patient/*.read", "launch"])
    }
    global smart_serverObj, smart_clientObj
    smart_clientObj = FHIRClient(settings=settings)
    smart_serverObj = FHIRServer(smart_clientObj, base_uri=request.values.get("iss"))
    smart_serverObj.get_capability()

    return redirect(smart_serverObj.authorize_uri)


@mocab_app.route("/fhir-app", methods=["GET"])
def callback():
    global smart_clientObj, smart_serverObj
    try:
        smart_serverObj.handle_callback(request.url)
    except Exception as e:
        return f"""<h1>Authorization Error</h1><p>{e}</p><p><a href="/">Start over</a></p>"""
    return redirect("http://localhost:8080")


def check_auth():
    global smart_serverObj
    try:
        return smart_serverObj.ready
    except AttributeError:
        return False
    except NameError:
        return False

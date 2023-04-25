from app import mocab_app
from fhirclient.client import FHIRClient
from flask import request, redirect

smart_clientObj: FHIRClient


@mocab_app.route("/launch", methods=['GET'])
def smart_launch():
    # TODO: Change redirect_uri
    global smart_clientObj
    settings = {
        'app_id': 'mocab_app',
        'api_base': request.values.get("iss"),
        'redirect_uri': f"http://{request.host}/fhir-app",
        'scope': " ".join(["patient/*.read", "launch"])
    }
    smart_clientObj = FHIRClient(settings=settings)

    return redirect(smart_clientObj.authorize_url)


@mocab_app.route("/fhir-app", methods=["GET"])
def callback():
    global smart_clientObj
    try:
        smart_clientObj.handle_callback(request.url)
    except Exception as e:
        return f"""<h1>Authorization Error</h1><p>{e}</p><p><a href="/">Start over</a></p>"""
    return "Authorized"


def check_auth():
    global smart_clientObj
    try:
        return smart_clientObj.ready
    except AttributeError:
        return False
    except NameError:
        return False

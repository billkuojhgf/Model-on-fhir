import requests
from config import configObject as conf


def call_api(model_name):
    """
    Description:
        This function is used to trigger the continuous training pipeline.
        It would be called by the scheduler.
    """

    api_url = f"http://localhost:{conf.get('flask_config').get('PORT')}/{model_name}"
    requests.get(api_url)

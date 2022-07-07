import requests
import pytest 

json_dummy_obj = {'somekey': 'somevalue'}
API_ROUTE="/api/sentry/webhook"

def test_local_post_request_to_hook():
    x = requests.post("http://localhost:5001" + API_ROUTE, json=json_dummy_obj)
    assert x.status_code == 200


def test_ngrok_post_request_to_hook():
    ngrok_url = 'https://85b8-178-237-233-8.eu.ngrok.io' + API_ROUTE

    x = requests.post(ngrok_url, json = json_dummy_obj)
    assert x.status_code == 200

import pytest
import requests

LOCAL_ADDR = "http://127.0.0.1:5000"
API_ROUTE = "/sentry/to-mattermost"
NGROK_HOST = "https://cb46-178-237-233-8.eu.ngrok.io"

local_request_json = {
    "action":"created", 
    "data":"some data", 
    "actor":
        {
            "type": "user",
            "id": 2038298,
            "name": "Carlos",
        }
    }


def test_hello():
    x = requests.get("http://127.0.0.1:5000/sentry/hello")
    assert x.status_code == 200


def test_local_post_request_to_hook():
    x = requests.post(LOCAL_ADDR + API_ROUTE, headers={"sentry-hook-resource":"error"}, json=local_request_json)   
    assert x.status_code == 200


def test_local_post_request_to_non_implemented_hook_returns_404():
    x = requests.post(LOCAL_ADDR + API_ROUTE, headers={"sentry-hook-resource":"issue"}, json=local_request_json)
    assert x.status_code == 404


def test_ngrok_request_to_hook():
    x = requests.post(NGROK_HOST + API_ROUTE, headers={"Content-type":"application/json", "sentry-hook-resource":"event_alert"}, json=local_request_json)   
    assert x.status_code == 200



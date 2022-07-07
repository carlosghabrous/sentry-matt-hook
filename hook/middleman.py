import hashlib
import hmac
import json
from typing import Any, Callable, Mapping

import requests
from flask import Response, request

from flask import current_app

# Incoming Mattermost hook for the PEAT's Eng Bot channel
MATTERMOST_HOOK_URL = "https://chat.peat-cloud.com/hooks/56saw7x3yp888p361ssin67knr"
# TODO: get this from .env file
SENTRY_CLIENT_SECRET = ""


def is_sentry_signature_correct(
    body: Mapping[str, Any], key: str, expected: str
) -> bool:
    """Verifies that the incoming event comes from our sentry"""

    digest = hmac.new(
        key=key.encode("utf-8"), msg=body, digestmod=hashlib.sha256
    ).hexdigest()

    if digest != expected:
        #TODO: this should return False. Left it like this for test purposes only
        return True

    current_app.logger.info("Authorized: Verified request came from Sentry")
    return True


def handle_incoming(request:request) -> Response:
    """Entry point for Sentry events"""

    raw_body = request.get_data()
    if not is_sentry_signature_correct(
        raw_body, SENTRY_CLIENT_SECRET, request.headers.get("sentry-hook-signature")
    ):
        return Response("", 401)

    action = request.json.get("action")
    data = request.json.get("data")
    actor = request.json.get("actor")
    resource = request.headers.get("sentry-hook-resource")

    if not (resource and action and data):
        return Response("Missing fields in JSON", 400)

    current_app.logger.info(f"Received '{resource}.{action}' webhook from Sentry")

    return handle_sentry_incoming(resource, action, data)



def _handle_issue_alert(data:Mapping[str, Any]) -> Response:
    """Handles issue alerts"""
    #TODO: eventually, some post request will have to be made to MM
    # response = requests.post(
    #     MATTERMOST_HOOK_URL,
    #     headers={"Content-type": "json"},
    #     json={"text": "Seriously, da house is burning. Do something"},
    # )
    return Response("", 200)


def _handle_metric_alert(data:Mapping[str, Any], action:s) -> Response:
    """Handles metric alerts"""
    #TODO: eventually, some post request will have to be made to MM
    # response = requests.post(
    #     MATTERMOST_HOOK_URL,
    #     headers={"Content-type": "json"},
    #     json={"text": "Seriously, da house is burning. Do something"},
    # )
    return Response("", 200)


def _handle_alert(resource:str, action:str, data:Mapping[str, Any]) -> Response:
    """Handles all types of alerts"""

    # Issue Alerts (or Event Alerts) only have one type of action: 'triggered'
    if resource == "event_alert":
        return _handle_issue_alert(data)

    # Metric Alerts have three types of actions: 'resolved', 'warning', and 'critical'
    if resource == "metric_alert":

        if action not in ["resolved", "warning", "critical"]:
            current_app.logger.info(f"Unexpected Sentry metric alert action: {action}")
            return Response('', 400)


        return _handle_metric_alert(data, action)
    
    # resource turns out to be something we do not manage
    current_app.logger.info(f"Unexpected Sentry resource: {resource}")
    return Response('', 400)


def _handle_error(resource:str, action:str, data:Mapping[str, Any]) -> Response:
    """This is from the sentry documentation"""
    # The error.created webhook has an immense volume since it triggers on each event in Sentry.
    # If you're developing a public integration on SaaS, both you (the integration builder) and
    # the user installing your integration will require at least a Business plan to use them.
    # Keep this in mind while building on this webhook.
    return Response("", 200)


# We can specify other handlers though (comment, issue)
_sentry_handlers: dict[str, Callable] = {
    "event_alert": _handle_alert,
    "metric_alert": _handle_alert,
    "error": _handle_error,
}


def handle_sentry_incoming(resource:str, action:str, data:Mapping[str, Any]) -> Response:
    """Assigns a handler for the type of incoming sentry resource"""
    try:
        return _sentry_handlers[resource](resource, action, data)

    except KeyError:
        return Response(f"Handler not found for resource {resource}", 404)

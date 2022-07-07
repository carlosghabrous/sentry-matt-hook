import hashlib
import hmac
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
    # digest = hmac.new(
    #     key=key.encode("utf-8"), msg=body, digestmod=hashlib.sha256
    # ).hexdigest()

    # if digest != expected:
    #     return False

    # current_app.logger.info("Authorized: Verified request came from Sentry")
    return True


def handle_incoming(request):
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


def _handle_alert(resource, action, data) -> Response:
    return Response("", 200)


def _handle_error(resource, action, data) -> Response:
    response = requests.post(
        MATTERMOST_HOOK_URL,
        headers={"Content-type": "json"},
        json={"text": "Seriously, da house is burning. Do something"},
    )
    return response


# We can specify other handlers though (comment, issue)
_sentry_handlers: dict[str, Callable] = {
    "event_alert": _handle_alert,
    "metric_alert": _handle_alert,
    "error": _handle_error,
}


def handle_sentry_incoming(resource, action, data) -> Response:
    try:
        return _sentry_handlers[resource](resource, action, data)

    except KeyError:
        return Response(f"Handler not found for resource {resource}", 404)

from flask import Blueprint, Response, current_app, request

import hook.middleman as middleman

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/sentry/webhook", methods=["POST"])
def webhook_index() -> Response:
    """Route that Sentry will use to send its event messages."""

    current_app.logger.info(f"received via webhook request: {request}")

    response = middleman.handle_incoming(request)

    if response.status_code != 200:
        current_app.logger.warning(f"{response.status_code}: {response}")
        return Response(
            "POST request to mattermost not successful", response.status_code
        )

    return Response("OK", 200)

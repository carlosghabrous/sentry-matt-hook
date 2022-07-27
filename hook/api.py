from flask import Blueprint, Flask, Response, current_app, request

import hook.middleman as middleman

app = Flask(__name__)
bp = Blueprint("api", __name__, url_prefix="/sentry")


@bp.route("/to-mattermost", methods=["POST"])
def to_mattermost() -> Response:
    """Route that Sentry will use to send its event messages."""

    current_app.logger.info(f"received via webhook request: {request}")

    response = middleman.handle_sentry_incoming(request)

    if response.status_code != 200:
        current_app.logger.warning(f"{response.status_code}: {response}")
        return Response(
            "POST request to mattermost not successful", response.status_code
        )

    return Response("OK", 200)


@bp.route("/hello", methods=["GET"])
def hello() -> Response:
    """A quick test to know if the flask setup is working, since I don't know what I'm doing"""
    return Response("OK", 200)


if __name__ == "__main__":
    app.run()

from logging.config import dictConfig

import requests
from flask import Flask, Response, request

import middleman

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)


app = Flask(__name__)


@app.route("/index", methods=["GET"])
def index() -> str:
    """Route added just to quickly test the Flask application and server"""
    return "Hello!"


@app.route("/api/sentry/webhook", methods=["POST"])
def webhook_index() -> Response:
    """Route that Sentry will use to send its event messages."""

    app.logger.info(f"received via webhook request: {request}")

    response = middleman.handle_incoming(request)

    if response.status_code != 200:
        app.logger.warning(f"{response.status_code}: {response}")
        return Response("POST request to mattermost not successful", response.status_code)

    return Response("", 200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

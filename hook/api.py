from flask import Flask, Response, current_app, request

from hook.middleman import bp

app = Flask(__name__)
app.register_blueprint(bp)


@app.route("/hello", methods=["GET"])
def hello() -> Response:
    """A quick test to know if the flask setup is working, since I don't know what I'm doing"""
    return Response("OK", 200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

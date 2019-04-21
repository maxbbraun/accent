from flask import Flask
from flask import Response
from flask import send_file
from io import BytesIO
from logging import exception
from time import time

from artwork import artwork_image
from city import city_image
from commute import commute_image
from epd import bwr_image
from epd import bwr_bytes
from g_calendar import calendar_image
from schedule import scheduled_delay
from schedule import scheduled_image

app = Flask(__name__)


def _send_png(image):
    """Creates a PNG response from the specified image."""

    # Encode the image to PNG bytes.
    buffer = BytesIO()
    image = bwr_image(image)
    image.save(buffer, format="png")
    buffer.seek(0)

    return send_file(buffer, mimetype="image/png", cache_timeout=0)


@app.route("/artwork")
def artwork():
    """Responds with a PNG version of the artwork image."""

    image = artwork_image()
    return _send_png(image)


@app.route("/city")
def city():
    """Responds with a PNG version of the city image."""

    image = city_image()
    return _send_png(image)


@app.route("/commute")
def commute():
    """Responds with a PNG version of the commute image."""

    image = commute_image()
    return _send_png(image)


@app.route("/calendar")
def calendar():
    """Responds with a PNG version of the calendar image."""

    image = calendar_image()
    return _send_png(image)


@app.route("/png")
def png():
    """Responds with a PNG version of the scheduled image."""

    image = scheduled_image()
    return _send_png(image)


@app.route("/epd")
def epd():
    """Responds with an e-paper display version of the scheduled image."""

    image = scheduled_image()
    data = bwr_bytes(image)
    buffer = BytesIO(data)

    return send_file(buffer, mimetype="application/octet-stream",
                     cache_timeout=0)


@app.route("/next")
def next():
    """Responds with the milliseconds until the next image."""

    milliseconds = scheduled_delay()
    return Response(str(milliseconds), mimetype="text/plain")


@app.errorhandler(500)
def server_error(e):
    """Logs the stack trace for server errors."""

    timestamp = int(time())
    message = "Internal Server Error @ %d" % timestamp
    exception(message)

    return message, 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)

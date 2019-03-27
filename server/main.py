from __future__ import division
from __future__ import print_function

from flask import Flask
from flask import Response
from flask import send_file
from io import BytesIO
from logging import exception
from numpy import argmin
from numpy import array
from numpy import packbits
from numpy import sum
from PIL import Image
from time import time

from artwork import get_artwork_image
from city import get_city_image
from commute import get_commute_image
from g_calendar import get_calendar_image
from schedule import get_scheduled_delay
from schedule import get_scheduled_image

# The dimensions of the display.
DISPLAY_WIDTH = 640
DISPLAY_HEIGHT = 384

# Black, white, and red as 8-bit RGB arrays.
BWR_8_BIT = array([[0, 0, 0], [255, 255, 255], [255, 0, 0]], dtype="uint8")

# Black, white and red as 2-bit BWR arrays.
BWR_2_BIT = array([[0, 0], [0, 1], [1, 1]], dtype="uint8")

app = Flask(__name__)


def _vq(obs, code_book):
    """Mimics scipy.cluster.vq.vq, which is not available."""

    repeated_shape = obs.shape[:1] + code_book.shape
    obs_repeated = obs.repeat(len(code_book), axis=0).reshape(repeated_shape)
    differences = obs_repeated.astype("float") - code_book
    distances = sum(differences ** 2, axis=2)
    return argmin(distances, axis=1)


def _get_indices(image):
    """Maps each pixel of an image to 0 (black), 1 (white), or 2 (red)."""

    image_data = array(image).reshape((DISPLAY_WIDTH * DISPLAY_HEIGHT, 3))
    return _vq(image_data, BWR_8_BIT)


def _send_png(image):
    """Creates a PNG response from the specified image."""

    # Map each color to the closest black, white, or red.
    indices = _get_indices(image)
    bwr_image_data = BWR_8_BIT[indices.reshape(
        (DISPLAY_HEIGHT, DISPLAY_WIDTH))]
    bwr_image = Image.fromarray(bwr_image_data)

    # Encode the image to PNG bytes.
    buffer = BytesIO()
    bwr_image.save(buffer, format="png")
    buffer.seek(0)

    return send_file(buffer, mimetype="image/png", cache_timeout=0)


@app.route("/artwork")
def artwork():
    """Responds with a PNG version of the artwork image."""

    image = get_artwork_image(DISPLAY_WIDTH, DISPLAY_HEIGHT)
    return _send_png(image)


@app.route("/city")
def city():
    """Responds with a PNG version of the city image."""

    image = get_city_image(DISPLAY_WIDTH, DISPLAY_HEIGHT)
    return _send_png(image)


@app.route("/commute")
def commute():
    """Responds with a PNG version of the commute image."""

    image = get_commute_image(DISPLAY_WIDTH, DISPLAY_HEIGHT)
    return _send_png(image)


@app.route("/calendar")
def calendar():
    """Responds with a PNG version of the calendar image."""

    image = get_calendar_image(DISPLAY_WIDTH, DISPLAY_HEIGHT)
    return _send_png(image)


@app.route("/png")
def png():
    """Responds with a PNG version of the scheduled image."""

    image = get_scheduled_image(DISPLAY_WIDTH, DISPLAY_HEIGHT)
    return _send_png(image)


@app.route("/epd")
def epd():
    """Responds with an e-paper display version of the scheduled image."""

    image = get_scheduled_image(DISPLAY_WIDTH, DISPLAY_HEIGHT)

    # Encode the image to 2-bit black, white, or red.
    indices = _get_indices(image)
    bwr_image_data = BWR_2_BIT[indices.reshape(
        (DISPLAY_HEIGHT * DISPLAY_WIDTH))]
    bwr_bytes = packbits(bwr_image_data).tostring()

    return send_file(BytesIO(bwr_bytes), mimetype="application/octet-stream",
                     cache_timeout=0)


@app.route("/next")
def next():
    """Responds with the milliseconds until the next image."""

    milliseconds = get_scheduled_delay()
    return Response(str(milliseconds), mimetype="text/plain")


@app.errorhandler(500)
def server_error(e):
    """Logs the stack trace for server errors."""

    timestamp = int(time())
    message = "Internal Server Error @ %d" % timestamp
    exception(message)

    return message, 500

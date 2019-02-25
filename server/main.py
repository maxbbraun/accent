from __future__ import division
from __future__ import print_function

from flask import Flask
from flask import Response
from flask import send_file
from io import BytesIO
from numpy import argmin
from numpy import array
from numpy import packbits
from numpy import sum
from PIL import Image

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


def vq(obs, code_book):
    """Mimics scipy.cluster.vq.vq, which is not available."""

    repeated_shape = obs.shape[:1] + code_book.shape
    obs_repeated = obs.repeat(len(code_book), axis=0).reshape(repeated_shape)
    differences = obs_repeated.astype("float") - code_book
    distances = sum(differences ** 2, axis=2)
    indices = argmin(distances, axis=1)
    return indices


def get_image():
    """Generates the image to show."""

    # Get the scheduled image.
    image = get_scheduled_image(DISPLAY_WIDTH, DISPLAY_HEIGHT)

    # Map each color to the closest black, white, or red.
    image_data = array(image).reshape((DISPLAY_WIDTH * DISPLAY_HEIGHT, 3))
    indices = vq(image_data, BWR_8_BIT)
    bwr_image_data = BWR_8_BIT[indices.reshape(
        (DISPLAY_HEIGHT, DISPLAY_WIDTH))]
    bwr_image = Image.fromarray(bwr_image_data)

    return bwr_image


@app.route("/png")
def png():
    """Responds with a PNG image for debugging."""

    image = get_image()

    # Encode the image to PNG bytes.
    buffer = BytesIO()
    image.save(buffer, format="png")
    buffer.seek(0)

    return send_file(buffer, mimetype="image/png", cache_timeout=0)


@app.route("/epd")
def epd():
    """Responds with image data encoded for the EPD."""

    image = get_image()

    # Encode the image to 2-bit black, white, or red.
    image_data = array(image).reshape((DISPLAY_WIDTH * DISPLAY_HEIGHT, 3))
    indices = vq(image_data, BWR_8_BIT)
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

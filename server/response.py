from flask import Response
from flask import send_file
from io import BytesIO

from epd import bwr_bytes
from epd import bwr_image


def gif_response(image):
    """Creates a Flask GIF response from the specified image."""

    buffer = BytesIO()
    image = bwr_image(image)
    image.save(buffer, format='gif')
    buffer.seek(0)

    return send_file(buffer, mimetype='image/gif', cache_timeout=0)


def epd_response(image):
    """Creates a Flask e-paper display response from the specified image."""

    data = bwr_bytes(image)
    buffer = BytesIO(data)

    return send_file(buffer, mimetype='application/octet-stream',
                     cache_timeout=0)


def text_response(text):
    """Creates a Flask text response."""

    return Response(text, mimetype='text/plain')

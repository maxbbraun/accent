from flask import Response
from flask import send_file
from flask import url_for
from io import BytesIO
from logging import exception
from PIL import Image

from content import ContentError
from epd import bwr_bytes
from epd import bwr_image
from graphics import draw_text
from graphics import SUBVARIO_CONDENSED_MEDIUM

# The color of the new user image background.
BACKGROUND_COLOR = (255, 0, 0)

# The color used for the new user image text.
TEXT_COLOR = (255, 255, 255)

# The image file for the computer in the settings image.
COMPUTER_FILE = 'assets/computer.gif'

# The position of the computer in the settings image.
COMPUTER_XY = (296, 145)

# The position of the link text in the settings image.
LINK_TEXT_XY = (0, 228)


def gif_response(image, size):
    """Creates a Flask GIF response from the specified image."""

    buffer = BytesIO()
    image = bwr_image(image, size)
    image.save(buffer, format='gif')
    buffer.seek(0)

    return send_file(buffer, mimetype='image/gif', cache_timeout=0)


def epd_response(image, size):
    """Creates a Flask e-paper display response from the specified image."""

    data = bwr_bytes(image, size)
    buffer = BytesIO(data)

    return send_file(buffer, mimetype='application/octet-stream',
                     cache_timeout=0)


def text_response(text):
    """Creates a Flask text response."""

    return Response(text, mimetype='text/plain')


def forbidden_response():
    """Creates a simple forbidden status response."""

    return Response(status=403)


def settings_url(key):
    """Creates the URL for user data settings."""

    return url_for('hello_get', key=key, _external=True)


def settings_response(key, image_func, size):
    """Creates an image response to start the new user flow."""

    # Draw the image with the link text and a computer.
    image = Image.new(mode='RGB', size=size,
                      color=BACKGROUND_COLOR)
    draw_text(settings_url(key),
              font_spec=SUBVARIO_CONDENSED_MEDIUM,
              text_color=TEXT_COLOR,
              xy=LINK_TEXT_XY,
              anchor='center_x',
              image=image)
    computer = Image.open(COMPUTER_FILE).convert(mode='RGBA')
    image.paste(computer, box=COMPUTER_XY, mask=computer)

    return image_func(image)


def content_response(content, image_response, user, size):
    """Creates an image response and handles the error case flow."""

    try:
        image = content.image(user, size)
        return image_response(image, size)
    except ContentError as e:
        exception('Failed to create %s content: %s' % (
            content.__class__.__name__, e))
        return settings_response(user.id, image_response, size)

from flask import Response
from flask import send_file
from flask import url_for
from io import BytesIO
from logging import exception
from logging import warning
from PIL import Image

from content import ContentError
from epd import adjust_xy
from epd import bwr_bytes
from epd import bwr_image
from epd import DEFAULT_DISPLAY_WIDTH
from epd import DEFAULT_DISPLAY_HEIGHT
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


def forbidden_response():
    """Creates a simple forbidden status response."""

    return Response(status=403)


def settings_url(key):
    """Creates the URL for user data settings."""

    return url_for('hello_get', key=key, _external=True)


def settings_response(key, image_func, width, height):
    """Creates an image response to start the new user flow."""

    # Draw the image with the link text and a computer.
    image = Image.new(mode='RGB', size=(width, height), color=BACKGROUND_COLOR)
    draw_text(settings_url(key),
              font_spec=SUBVARIO_CONDENSED_MEDIUM,
              text_color=TEXT_COLOR,
              xy=adjust_xy(*LINK_TEXT_XY, width, height),
              anchor='center_x',
              image=image)
    computer = Image.open(COMPUTER_FILE).convert(mode='RGBA')
    image.paste(computer, box=adjust_xy(*COMPUTER_XY, width, height),
                mask=computer)

    return image_func(image)


def content_response(content, image_response, user, width, height):
    """Creates an image response and handles the error case flow."""

    try:
        image = content.image(user, width, height)
        return image_response(image)
    except ContentError as e:
        exception('Failed to create %s content: %s' % (
            content.__class__.__name__, e))
        return settings_response(user.id, image_response, width, height)


def display_size(request):
    """Extracts the display size from the request or uses defaults."""

    width = request.args.get('width', default=DEFAULT_DISPLAY_WIDTH)
    height = request.args.get('height', default=DEFAULT_DISPLAY_HEIGHT)

    try:
        return int(width), int(height)
    except ValueError as e:
        warning('Malformed display size: %sx%s' % (width, height))
        return DEFAULT_DISPLAY_WIDTH, DEFAULT_DISPLAY_HEIGHT

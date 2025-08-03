from flask import Response
from flask import send_file
from flask import url_for
from io import BytesIO
from logging import exception
from logging import warning
from PIL import Image

from content import ContentError
from epd import adjust_xy
from epd import ensure_rgb
from epd import to_epd_bytes
from epd import to_epd_image
from epd import DEFAULT_DISPLAY_HEIGHT
from epd import DEFAULT_DISPLAY_WIDTH
from epd import DEFAULT_DISPLAY_VARIANT
from epd import DISPLAY_VARIANTS
from graphics import draw_text
from graphics import SUBVARIO_CONDENSED_MEDIUM


def rotate_dimensions(width, height, rotation):
    """Applies the rotation, swapping width and height if needed."""

    if rotation in [90, 270]:
        return height, width

    return width, height


def rotate_image(image, rotation):
    """Applies rotation to an image to match the display orientation."""

    if not rotation in [0, 90, 180, 270]:
        raise ContentError('Invalid rotation: %s' % rotation)

    return image.rotate(rotation, expand=True)


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


def gif_response(image, variant):
    """Creates a Flask GIF response from the specified image."""

    buffer = BytesIO()
    image = to_epd_image(image, variant)
    image.save(buffer, format='gif')
    buffer.seek(0)

    return send_file(buffer, mimetype='image/gif', max_age=0)


def epd_response(image, variant):
    """Creates a Flask e-paper display response from the specified image."""

    data = to_epd_bytes(image, variant)
    buffer = BytesIO(data)

    return send_file(buffer, mimetype='application/octet-stream', max_age=0)


def text_response(text):
    """Creates a Flask text response."""

    return Response(text, mimetype='text/plain')


def forbidden_response():
    """Creates a simple forbidden status response."""

    return Response(status=403)


def settings_url(key):
    """Creates the URL for user data settings."""

    return url_for('hello_get', key=key, _external=True)


def settings_response(key, image_func, width, height, variant):
    """Creates an image response to start the new user flow."""

    # Draw the image with the link text and a computer.
    with Image.new(mode='RGB',
                   size=(width, height),
                   color=BACKGROUND_COLOR) as image:
        draw_text(settings_url(key),
                font_spec=SUBVARIO_CONDENSED_MEDIUM,
                text_color=TEXT_COLOR,
                xy=adjust_xy(*LINK_TEXT_XY, width, height),
                anchor='center_x',
                image=image)
        with ensure_rgb(Image.open(COMPUTER_FILE), alpha=True) as computer:
            image.paste(computer,
                        box=adjust_xy(*COMPUTER_XY, width, height),
                        mask=computer)

        return image_func(image, variant)


def content_response(content, image_response, user, width, height, variant):
    """Creates an image response and handles the error case flow."""

    # Get the user's rotation setting.
    if user:
        try:
            rotation = user.get('rotation')
        except KeyError:
            rotation = 0
    else:
        rotation = 0

    # Apply the rotation to the dimensions for content generation.
    rotated_width, rotated_height = rotate_dimensions(width, height, rotation)

    try:
        # Generate the image with the rotated dimensions.
        with content.image(user, rotated_width, rotated_height, variant) as image:
            # Correct the rotation of the image content itself.
            image = rotate_image(image, rotation)

            return image_response(image, variant)
    except ContentError as e:
        exception('Failed to create %s content: %s' % (
            content.__class__.__name__, e))
        return settings_response(user.id, image_response, width, height,
                                 variant)


def display_metadata(request):
    """Extracts the display metadata from the request or uses defaults."""

    width = request.args.get('width', default=DEFAULT_DISPLAY_WIDTH)
    height = request.args.get('height', default=DEFAULT_DISPLAY_HEIGHT)
    variant = request.args.get('variant', default=DEFAULT_DISPLAY_VARIANT)

    if variant not in DISPLAY_VARIANTS:
        warning('Invalid display variant: %s' % variant)
        variant = DEFAULT_DISPLAY_VARIANT

    try:
        return int(width), int(height), variant
    except ValueError:
        warning('Malformed display size: %sx%s' % (width, height))
        return DEFAULT_DISPLAY_WIDTH, DEFAULT_DISPLAY_HEIGHT, variant

from flask import Response
from flask import request
from functools import wraps
from PIL import Image

from epd import DISPLAY_WIDTH
from epd import DISPLAY_HEIGHT
from firestore import Firestore
from graphics import draw_text
from graphics import SUBVARIO_CONDENSED_MEDIUM
from response import text_response

# The URL to show for starting a new user flow. Arguments are host and key.
NEW_USER_URL = "https://%s/hello/%s"

# The color of the new user image background.
BACKGROUND_COLOR = (255, 0, 0)

# The color used for the new user image text.
TEXT_COLOR = (255, 255, 255)


def _forbidden_response():
    """Creates a simple forbidden status response."""

    return Response(status=403)


def _new_user_response(key, image_func):
    """Creates an image response to start the new user flow."""

    # Draw the image with the link text.
    image = Image.new(mode="RGB", size=(DISPLAY_WIDTH, DISPLAY_HEIGHT),
                      color=BACKGROUND_COLOR)
    draw_text(NEW_USER_URL % (request.host, key),
              font_spec=SUBVARIO_CONDENSED_MEDIUM,
              text_color=TEXT_COLOR,
              anchor="center",
              image=image)

    return image_func(image)


def user_auth(image_func=None):
    """A decorator for Flask route functions to enforce user authentication."""

    firestore = Firestore()

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Look for a key debug request argument first.
                key = request.args["key"]
            except KeyError:
                # Otherwise, expect a basic access authentication header.
                authorization = request.authorization
                if not authorization:
                    return _forbidden_response()
                key = authorization["password"]

            # Look up the user from the key.
            user = firestore.user(key)
            if not user:
                if image_func:
                    # For image requests, start the new user flow.
                    return _new_user_response(key, image_func)
                else:
                    # Otherwise, return a forbidden response.
                    return _forbidden_response()

            # Inject the user into the function arguments.
            kwargs["user"] = user
            return func(*args, **kwargs)

        return wrapper

    return decorator

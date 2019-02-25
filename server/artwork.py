from glob import glob
from logging import info
from PIL import Image
from random import choice
from random import randint

# The directory containing static artwork images.
IMAGES_DIR = "artwork"


def get_artwork_image(width, height):
    """Generates a random crop from a random artwork image."""

    # Load a random image.
    filename = choice(glob("%s/*.gif" % IMAGES_DIR))
    info("Using artwork file: %s" % filename)
    image = Image.open(filename)
    image = image.convert("RGB")

    # Crop the image to a random display-sized area.
    x = randint(0, max(0, image.size[0] - width))
    y = randint(0, max(0, image.size[1] - height))
    image = image.crop((x, y, x + width, y + height))

    return image

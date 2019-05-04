from glob import glob
from logging import info
from os.path import join as path_join
from PIL import Image
from random import choice
from random import randint

from epd import DISPLAY_WIDTH
from epd import DISPLAY_HEIGHT

# The directory containing static artwork images.
IMAGES_DIR = 'assets/artwork'

# The file extension of all artwork image files.
IMAGE_EXTENSION = 'gif'


class Artwork:
    """A collection of randomly selected image artwork."""

    def __init__(self, user):
        pass

    def image(self):
        """Generates an artwork image."""

        # Load a random image.
        paths = glob(path_join(IMAGES_DIR, '*.%s' % IMAGE_EXTENSION))
        filename = choice(paths)
        info('Using artwork file: %s' % filename)
        image = Image.open(filename)
        image = image.convert('RGB')

        # Crop the image to a random display-sized area.
        x = randint(0, max(0, image.width - DISPLAY_WIDTH))
        y = randint(0, max(0, image.height - DISPLAY_HEIGHT))
        image = image.crop((x, y, x + DISPLAY_WIDTH, y + DISPLAY_HEIGHT))

        return image

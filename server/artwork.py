from glob import glob
from logging import info
from os.path import join as path_join
from PIL import Image
from random import choice
from random import randint

from content import ImageContent

# The directory containing static artwork images.
IMAGES_DIR = 'assets/artwork'

# The file extension of all artwork image files.
IMAGE_EXTENSION = 'gif'


class Artwork(ImageContent):
    """A collection of randomly selected image artwork."""

    def image(self, _, width, height):
        """Generates an artwork image."""

        # Load a random image.
        paths = glob(path_join(IMAGES_DIR, '*.%s' % IMAGE_EXTENSION))
        filename = choice(paths)
        info('Using artwork file: %s' % filename)
        image = Image.open(filename)
        image = image.convert('RGB')

        # Crop the image to a random display-sized area.
        x = randint(0, max(0, image.width - width))
        y = randint(0, max(0, image.height - height))
        image = image.crop((x, y, x + width, y + height))

        return image

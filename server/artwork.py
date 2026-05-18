from glob import glob
from logging import info
from os.path import join as path_join
from PIL import Image
from random import choice
from random import randint

from content import ImageContent
from epd import ensure_rgb

# The directory containing static artwork images.
IMAGES_DIR = 'assets/artwork'

# The file extension of all artwork image files.
IMAGE_EXTENSION = 'gif'


class Artwork(ImageContent):
    """A collection of randomly selected image artwork."""

    def image(self, user, width, height, variant):
        """Generates an artwork image."""

        # Load a random image.
        paths = glob(path_join(IMAGES_DIR, '*.%s' % IMAGE_EXTENSION))
        filename = choice(paths)
        info('Using artwork file: %s' % filename)

        with ensure_rgb(Image.open(filename)) as image:
            # Crop the image to a random display-sized area.
            x = randint(0, max(0, image.width - width))
            y = randint(0, max(0, image.height - height))
            with image.crop((x, y, x + width, y + height)) as cropped_image:

                # The source artwork is already quantized (no dithering).
                return cropped_image.convert(
                    'P',
                    dither=Image.Dither.NONE,
                    palette=Image.Palette.ADAPTIVE)

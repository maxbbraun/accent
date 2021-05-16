from glob import glob
from logging import info
from os.path import join as path_join
from PIL import Image
from random import choice
from random import randint

from content import ImageContent
from epd import edge_color

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

        # Larger images are cropped to a random display-sized area.
        # Smaller images are centered in the middle of the display.
        if width > image.width:
            x = int((width - image.width) / 2)
        else:
            x = -randint(0, image.width - width)
        if height > image.height:
            y = int((height - image.height) / 2)
        else:
            y = -randint(0, image.height - height)
        
        output = Image.new('RGB', (width, height), color=edge_color(image))
        output.paste(image, (x, y))
        return output

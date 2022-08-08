from numpy import argmax
from numpy import array
from numpy import packbits
from numpy import uint8
from numpy import unique
from PIL import Image
from scipy.cluster.vq import vq

# The default width of the display in pixels.
DEFAULT_DISPLAY_WIDTH = 640

# The default height of the display in pixels.
DEFAULT_DISPLAY_HEIGHT = 384

# Black, white, and red as 8-bit RGB arrays.
BWR_8_BIT = array([[0, 0, 0], [255, 255, 255], [255, 0, 0]], dtype=uint8)

# Black, white and red as 2-bit BWR arrays.
BWR_2_BIT = array([[0, 0], [0, 1], [1, 1]], dtype=uint8)


def _color_indices(image):
    """Maps each pixel of an image to 0 (black), 1 (white), or 2 (red)."""

    image_data = array(image).reshape((image.width * image.height, 3))
    indices, _ = vq(image_data, BWR_8_BIT)
    return indices


def bwr_image(image):
    """Converts the image's colors to the closest black, white, or red."""

    indices = _color_indices(image)
    bwr_image_data = BWR_8_BIT[indices.reshape((image.height, image.width))]
    return Image.fromarray(bwr_image_data)


def bwr_bytes(image):
    """Converts the image to the closest 2-bit black, white, or red bytes."""

    indices = _color_indices(image)
    bwr_image_data = BWR_2_BIT[indices.reshape((image.height * image.width))]
    return packbits(bwr_image_data)


def adjust_xy(x, y, width, height):
    """Converts coordinates expressed relative to the default display size."""

    # Adjust by half the difference for a center crop.
    x += (width - DEFAULT_DISPLAY_WIDTH) // 2
    y += (height - DEFAULT_DISPLAY_HEIGHT) // 2

    return x, y


def edge_color(image):
    """Returns the most common color (r, g, b) of the image edge.

    Looks at the pixels at the edge of the image and returns the most
    common color. This is then used as a background color in case display
    size is larger than the image size.
    """
    i = array(bwr_image(image))
    edge = array(
        list(i[0]) +  # top
        list(i[-1]) +  # bottom
        [r[0] for r in i] + # left
        [r[-1] for r in i]) # right
    values, counts = unique(edge, axis=0, return_counts=True)
    return tuple(values[argmax(counts)])

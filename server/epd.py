from numpy import array
from numpy import packbits
from numpy import uint8
from PIL import Image
from scipy.cluster.vq import vq

# The width of the display in pixels.
DISPLAY_WIDTH = 640

# The height of the display in pixels.
DISPLAY_HEIGHT = 384

# Black, white, and red as 8-bit RGB arrays.
BWR_8_BIT = array([[0, 0, 0], [255, 255, 255], [255, 0, 0]], dtype=uint8)

# Black, white and red as 2-bit BWR arrays.
BWR_2_BIT = array([[0, 0], [0, 1], [1, 1]], dtype=uint8)


def _color_indices(image, size):
    """Maps each pixel of an image to 0 (black), 1 (white), or 2 (red)."""

    image_data = array(image).reshape((size[0] * size[1], 3))
    indices, _ = vq(image_data, BWR_8_BIT)
    return indices


def bwr_image(image, size):
    """Converts the image's colors to the closest black, white, or red."""

    indices = _color_indices(image, size)
    bwr_image_data = BWR_8_BIT[indices.reshape(
        (size[1], size[0]))]
    return Image.fromarray(bwr_image_data)


def bwr_bytes(image, size):
    """Converts the image to the closest 2-bit black, white, or red bytes."""

    indices = _color_indices(image, size)
    bwr_image_data = BWR_2_BIT[indices.reshape(
        (size[0] * size[1]))]
    return packbits(bwr_image_data)

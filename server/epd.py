from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from numpy import argmin
from numpy import array
from numpy import sum as np_sum
from numpy import packbits
from numpy import uint8
from PIL import Image

# The width of the display in pixels.
DISPLAY_WIDTH = 640

# The height of the display in pixels.
DISPLAY_HEIGHT = 384

# Black, white, and red as 8-bit RGB arrays.
BWR_8_BIT = array([[0, 0, 0], [255, 255, 255], [255, 0, 0]], dtype=uint8)

# Black, white and red as 2-bit BWR arrays.
BWR_2_BIT = array([[0, 0], [0, 1], [1, 1]], dtype=uint8)


def _vq(obs, code_book):
    """Mimics scipy.cluster.vq.vq, which is not available."""

    repeated_shape = obs.shape[:1] + code_book.shape
    obs_repeated = obs.repeat(len(code_book), axis=0).reshape(repeated_shape)
    differences = obs_repeated.astype("float") - code_book
    distances = np_sum(differences ** 2, axis=2)
    return argmin(distances, axis=1)


def _color_indices(image):
    """Maps each pixel of an image to 0 (black), 1 (white), or 2 (red)."""

    image_data = array(image).reshape((DISPLAY_WIDTH * DISPLAY_HEIGHT, 3))
    return _vq(image_data, BWR_8_BIT)


def bwr_image(image):
    """Converts the image's colors to the closest black, white, or red."""

    indices = _color_indices(image)
    bwr_image_data = BWR_8_BIT[indices.reshape(
        (DISPLAY_HEIGHT, DISPLAY_WIDTH))]
    return Image.fromarray(bwr_image_data)


def bwr_bytes(image):
    """Converts the image to the closest 2-bit black, white, or red bytes."""

    indices = _color_indices(image)
    bwr_image_data = BWR_2_BIT[indices.reshape(
        (DISPLAY_HEIGHT * DISPLAY_WIDTH))]
    return packbits(bwr_image_data).tostring()

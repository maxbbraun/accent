from numpy import array
from numpy import packbits
from numpy import uint8
from PIL import Image
from PIL import ImagePalette
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
    """Maps each image pixel to the index of the closest palette color."""

    # Apply dithering, which will not affect already quantized images.
    image = image.convert(mode='P', palette=epd_palette(),
                          dither=Image.FLOYDSTEINBERG)
    image = image.convert('RGB')
    image_data = array(image).reshape((image.width * image.height, 3))
    indices, _ = vq(image_data, BWR_8_BIT)

    return indices


def epd_palette():
    """Returns the RGB palette used by the display."""

    colors = [tuple(c) for c in BWR_8_BIT]
    return ImagePalette.ImagePalette(mode='RGB', palette=colors)


def to_epd_image(image):
    """Converts the image's colors to the closest palette color."""

    indices = _color_indices(image)
    epd_image_data = BWR_8_BIT[indices.reshape((image.height, image.width))]
    return Image.fromarray(epd_image_data)


def to_epd_bytes(image):
    """Converts the image to the closest 2-bit palette color bytes."""

    indices = _color_indices(image)
    epd_image_data = BWR_2_BIT[indices.reshape((image.height * image.width))]
    return packbits(epd_image_data)


def adjust_xy(x, y, width, height):
    """Converts coordinates expressed relative to the default display size."""

    # Adjust by half the difference for a center crop.
    x += (width - DEFAULT_DISPLAY_WIDTH) // 2
    y += (height - DEFAULT_DISPLAY_HEIGHT) // 2

    return x, y

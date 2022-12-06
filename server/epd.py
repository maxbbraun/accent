from dithering import dither
from numpy import array
from numpy import packbits
from numpy import uint8
from PIL import Image
from scipy.cluster.vq import vq

# The default width of the display in pixels.
DEFAULT_DISPLAY_WIDTH = 640

# The default height of the display in pixels.
DEFAULT_DISPLAY_HEIGHT = 384

# The variants of supported displays.
DISPLAY_VARIANTS = ['bwr', '7color']

# The default display variant.
DEFAULT_DISPLAY_VARIANT = 'bwr'

# Black, white, and red as an 8-bit RGB array.
PALETTE_BWR = array([[0, 0, 0], [255, 255, 255], [255, 0, 0]], dtype=uint8)

# Black, white and red as a 2-bit index array.
ENCODING_BWR = array([[0, 0], [0, 1], [1, 1]], dtype=uint8)

# 7-color (black, white, green, blue, red, yellow, orange) as an 8-bit RGB
# array.
PALETTE_7COLOR = array([[16, 16, 16], [239, 239, 239], [27, 120, 27],
                        [54, 43, 162], [180, 21, 21], [224, 212, 13],
                        [193, 103, 13]], dtype=uint8)

# 7-color (black, white, green, blue, red, yellow, orange) as a 3-bit index
# array.
ENCODING_7COLOR = array([[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 0, 0],
                         [1, 0, 1], [1, 1, 0]], dtype=uint8)


def _dither(image, palette):
    """Dithers the image using the Floyd-Steinberg algorithm."""

    # Call the C extension to iterate over all image pixels efficiently.
    image = image.convert('RGB')
    pixels = array(image)
    dither(pixels, palette)

    return Image.fromarray(pixels)


def _color_indices(image, variant):
    """Maps each image pixel to the index of the closest palette color."""

    # Apply dithering unless the image is already quantized.
    palette = epd_palette(variant)
    if image.mode not in ('1', 'L', 'P'):
        image = _dither(image, palette)

    # Map each pixel to the closest palette color.
    image = image.convert('RGB')
    image_data = array(image).reshape((image.width * image.height, 3))
    indices, _ = vq(image_data, palette)

    return indices


def epd_palette(variant):
    """Returns the RGB palette used by the display."""

    if variant == 'bwr':
        return PALETTE_BWR
    elif variant == '7color':
        return PALETTE_7COLOR
    else:
        raise ValueError('Unsupported display variant: %s' % variant)


def epd_encoding(variant):
    """Returns the color encoding used to send data to the display."""

    if variant == 'bwr':
        return ENCODING_BWR
    elif variant == '7color':
        return ENCODING_7COLOR
    else:
        raise ValueError('Unsupported display variant: %s' % variant)


def to_epd_image(image, variant):
    """Converts the image's colors to the closest palette color."""

    indices = _color_indices(image, variant)
    palette = epd_palette(variant)
    epd_image_data = palette[indices.reshape((image.height, image.width))]
    return Image.fromarray(epd_image_data)


def to_epd_bytes(image, variant):
    """Converts the image to the closest 2-bit palette color bytes."""

    indices = _color_indices(image, variant)
    encoding = epd_encoding(variant)
    epd_image_data = encoding[indices.reshape((image.height * image.width))]
    return packbits(epd_image_data)


def adjust_xy(x, y, width, height):
    """Converts coordinates expressed relative to the default display size."""

    # Adjust by half the difference for a center crop.
    x += (width - DEFAULT_DISPLAY_WIDTH) // 2
    y += (height - DEFAULT_DISPLAY_HEIGHT) // 2

    return x, y

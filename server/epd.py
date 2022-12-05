from dithering import dither
from numpy import array
from numpy import frombuffer
from numpy import packbits
from numpy import uint8
from PIL import Image
from PIL import ImagePalette
from scipy.cluster.vq import vq

# The default width of the display in pixels.
DEFAULT_DISPLAY_WIDTH = 640

# The default height of the display in pixels.
DEFAULT_DISPLAY_HEIGHT = 384

# Black, white, and red as an 8-bit RGB array.
BWR_8_BIT = array([[0, 0, 0], [255, 255, 255], [255, 0, 0]], dtype=uint8)

# Black, white and red as a 2-bit index array.
BWR_2_BIT = array([[0, 0], [0, 1], [1, 1]], dtype=uint8)


def _dither(image, palette):
    """Dithers the image using the Floyd-Steinberg algorithm."""

    # Call the C extension to iterate over all image pixels efficiently.
    pixels = array(image)
    dither(pixels, palette)

    return Image.fromarray(pixels)


def _color_indices(image):
    """Maps each image pixel to the index of the closest palette color."""

    # Apply dithering, which will not affect already quantized images.
    palette = epd_palette()
    image = _dither(image, palette)
    image_data = array(image).reshape((image.width * image.height, 3))
    indices, _ = vq(image_data, palette)

    return indices


def epd_palette(for_pil=False):
    """Returns the RGB palette used by the display."""

    palette = BWR_8_BIT

    if not for_pil:
        return palette

    # Convert the palette to the PIL format.
    palette_data = list(palette.flatten())
    return ImagePalette.ImagePalette(mode='RGB', palette=palette_data)


def epd_encoding():
    """Returns the color encoding used to send data to the display."""

    return BWR_2_BIT


def to_epd_image(image):
    """Converts the image's colors to the closest palette color."""

    indices = _color_indices(image)
    palette = epd_palette()
    epd_image_data = palette[indices.reshape((image.height, image.width))]
    return Image.fromarray(epd_image_data)


def to_epd_bytes(image):
    """Converts the image to the closest 2-bit palette color bytes."""

    indices = _color_indices(image)
    encoding = epd_encoding()
    epd_image_data = encoding[indices.reshape((image.height * image.width))]
    return packbits(epd_image_data)


def adjust_xy(x, y, width, height):
    """Converts coordinates expressed relative to the default display size."""

    # Adjust by half the difference for a center crop.
    x += (width - DEFAULT_DISPLAY_WIDTH) // 2
    y += (height - DEFAULT_DISPLAY_HEIGHT) // 2

    return x, y

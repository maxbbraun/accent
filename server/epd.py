from dithering import dither
from numpy import array, packbits, uint8, argmin, sum as npsum, zeros
from PIL import Image

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

# 7-color (black, white, green, blue, red, yellow, orange) as a 4-bit index
# array.
ENCODING_7COLOR = array([[0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0],
                         [0, 0, 1, 1], [0, 1, 0, 0], [0, 1, 0, 1],
                         [0, 1, 1, 0]], dtype=uint8)


def _find_closest_colors(pixels, palette):
    """Memory-efficient replacement for scipy.cluster.vq.vq.
    
    Finds the closest palette color for each pixel using chunked processing
    to minimize memory usage.
    """
    num_pixels = pixels.shape[0]
    indices = zeros(num_pixels, dtype=uint8)
    
    # Process in chunks to avoid creating large distance matrices
    chunk_size = 1000  # Process 1000 pixels at a time
    
    for i in range(0, num_pixels, chunk_size):
        end_idx = min(i + chunk_size, num_pixels)
        chunk = pixels[i:end_idx]
        
        # Calculate squared Euclidean distances for this chunk
        # chunk shape: (chunk_size, 3), palette shape: (num_colors, 3)
        # We want distances shape: (chunk_size, num_colors)
        
        # Expand dimensions for broadcasting: chunk[:, None, :] - palette[None, :, :]
        chunk_expanded = chunk[:, None, :]  # (chunk_size, 1, 3)
        palette_expanded = palette[None, :, :]  # (1, num_colors, 3)
        
        # Calculate squared differences
        diff = chunk_expanded - palette_expanded  # (chunk_size, num_colors, 3)
        distances_sq = npsum(diff * diff, axis=2)  # (chunk_size, num_colors)
        
        # Find indices of minimum distances
        chunk_indices = argmin(distances_sq, axis=1)
        indices[i:end_idx] = chunk_indices
        
        # Clean up chunk variables to free memory
        del chunk, chunk_expanded, palette_expanded, diff, distances_sq, chunk_indices
    
    return indices


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
    # Avoid redundant RGB conversion if already done in _dither
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Use view instead of reshape to avoid copying data
    image_data = array(image)
    image_data = image_data.reshape(-1, 3)
    indices = _find_closest_colors(image_data, palette)
    
    # Clean up the temporary array to free memory immediately
    del image_data

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

# To generate client code for static images, run:
# $ pip install absl-py
# $ python client_image.py --input=assets/client/error.gif

from absl import app
from absl import flags
from ntpath import basename
from numpy import array
from numpy import packbits
from numpy import uint8
from numpy import where
from os import extsep
from PIL import Image
from scipy.cluster.vq import vq
from six import iterbytes

FLAGS = flags.FLAGS
flags.DEFINE_string('input', 'assets/client/error.gif',
                    'The path to the input image.')
flags.DEFINE_enum('background', 'red', ['black', 'white', 'red'],
                  'The background color of the image.')

# The number of columns in the file.
COLUMNS = 80

# The string format for each line of image data.
LINE_FORMAT = '    "%s"'

# The string format for each byte of image data.
BYTE_FORMAT = '\\x%02X'

# The number of bytes per line.
BYTES_PER_LINE = (COLUMNS - len(LINE_FORMAT % '')) // len(BYTE_FORMAT % 0)

# The mapping of color names to their GxEPD2 encoding.
COLOR_LUT = {'black': 0x0000, 'white': 0xFFFF, 'red': 0xF800}

# The mapping of color names to their channel index.
CHANNEL_LUT = {'black': 0, 'white': 1, 'red': 2}

# The 8-bit RGB values corresponding to black, white, and red.
BWR_8_BIT = array([[0, 0, 0], [255, 255, 255], [255, 0, 0]], dtype=uint8)


def encode(image, color):
    """Encodes the specified color channel of the image into 1-bit pixels."""

    image_data = array(image).reshape((image.width * image.height, 3))
    indices, _ = vq(image_data, BWR_8_BIT)
    channel = CHANNEL_LUT[color]
    bits = where(indices == channel, 1, 0)
    bytes = packbits(bits)

    return bytes


def write_bytes(variable_name, bytes, output):
    """Writes the variable initialized with the specified bytes to output."""

    output.write('const PROGMEM uint8_t %s[] =\n' % variable_name)

    bytes_range = range(0, len(bytes), BYTES_PER_LINE)
    for i in bytes_range:
        line = ''
        for j in iterbytes(bytes[i:i + BYTES_PER_LINE]):
            line += BYTE_FORMAT % j
        if i == bytes_range[-1]:
            line_format = LINE_FORMAT + ';'
        else:
            line_format = LINE_FORMAT
        output.write(line_format % line)
        output.write('\n')


def main(_):
    source_filename = basename(FLAGS.input)
    base_name = source_filename.split(extsep)[0]

    output_path = '../client/%sImage.h' % base_name.title()
    include_guard = '%s_IMAGE_H' % base_name.upper()
    black_image_variable_name = 'k%sImageBlack' % base_name.title()
    red_image_variable_name = 'k%sImageRed' % base_name.title()
    background_variable_name = 'k%sBackground' % base_name.title()
    width_variable_name = 'k%sWidth' % base_name.title()
    height_variable_name = 'k%sHeight' % base_name.title()
    script_filename = basename(__file__)

    with open(output_path, 'w') as output:
        output.write('#ifndef %s\n' % include_guard)
        output.write('#define %s\n\n' % include_guard)

        image = Image.open(FLAGS.input).convert('RGB')
        assert image.width % 8 == 0, 'Image width must be a multiple of 8'

        output.write('// Generated from "%s" using "%s".\n' % (
            source_filename, script_filename))
        output.write('const uint16_t %s = 0x%02X;  // %s\n' % (
            background_variable_name, COLOR_LUT[FLAGS.background],
            FLAGS.background))
        output.write('const uint16_t %s = %d;\n' % (width_variable_name,
                                                    image.width))
        output.write('const uint16_t %s = %d;\n' % (height_variable_name,
                                                    image.height))

        black_bytes = encode(image, 'black')
        write_bytes(black_image_variable_name, black_bytes, output)

        red_bytes = encode(image, 'red')
        write_bytes(red_image_variable_name, red_bytes, output)

        output.write('\n#endif  // %s\n' % include_guard)


if __name__ == '__main__':
    app.run(main)

# The error image is embedded in the client code. To update it, run:
# $ pip install absl-py
# $ python error_image.py --input=./assets/error.gif > ../client/error_image.h

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import app
from absl import flags
from PIL import Image
from six import iterbytes

from epd import bwr_bytes

FLAGS = flags.FLAGS
flags.DEFINE_string("input", "./assets/error.gif",
                    "The path to the input image.")
flags.DEFINE_string("include_guard", "error_image_h",
                    "The include guard for the header file.")
flags.DEFINE_string("variable_name", "error_image",
                    "The variable name for the image data array.")
flags.DEFINE_string("variable_comment", (
    "// A 2-bit image to show when an error occurs.\n"
    "// Based on this graphic: "
    "https://db.eboy.com/spritebox/hi9BihdXY4TjkeHrT"),
    "The comment for the image data array.")

# The number of columns in the file.
COLUMNS = 80

# The string format for each line of image data.
LINE_FORMAT = "    \"%s\""

# The string format for each byte of image data.
BYTE_FORMAT = "\\x%02x"

# The number of bytes per line.
BYTES_PER_LINE = (COLUMNS - len(LINE_FORMAT % "")) // len(BYTE_FORMAT % 0)


def main(_):
    print("#ifndef %s" % FLAGS.include_guard)
    print("#define %s" % FLAGS.include_guard)
    print()

    print(FLAGS.variable_comment)
    print("const char %s[] =" % FLAGS.variable_name)

    image = Image.open(FLAGS.input).convert("RGB")
    data = bwr_bytes(image)

    data_range = range(0, len(data), BYTES_PER_LINE)
    for i in data_range:
        line = ""
        for j in iterbytes(data[i:i + BYTES_PER_LINE]):
            line += BYTE_FORMAT % j
        if i == data_range[-1]:
            line_format = LINE_FORMAT + ";"
        else:
            line_format = LINE_FORMAT
        print(line_format % line)

    print()
    print("#endif  // %s" % FLAGS.include_guard)


if __name__ == '__main__':
    app.run(main)

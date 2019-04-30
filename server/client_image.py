# To generate client code for static images, run:
# $ pip install absl-py
# $ python client_image.py --input=assets/client/error.gif

from absl import app
from absl import flags
from ntpath import basename
from ntpath import splitext
from PIL import Image
from six import iterbytes

from epd import bwr_bytes

FLAGS = flags.FLAGS
flags.DEFINE_string("input", "assets/client/error.gif",
                    "The path to the input image.")

# The string format of the output file path.
OUTPUT_PATH_FORMAT = "../client/%s_image.h"

# The string format of the variable name.
VARIABLE_NAME_FORMAT = "%s_image"

# The number of columns in the file.
COLUMNS = 80

# The string format for each line of image data.
LINE_FORMAT = "    \"%s\""

# The string format for each byte of image data.
BYTE_FORMAT = "\\x%02x"

# The number of bytes per line.
BYTES_PER_LINE = (COLUMNS - len(LINE_FORMAT % "")) // len(BYTE_FORMAT % 0)


def main(_):
    source_filename = basename(FLAGS.input)
    base_name = splitext(source_filename)[0]
    output_path = OUTPUT_PATH_FORMAT % base_name
    include_guard = basename(output_path).replace(".", "_")
    variable_name = VARIABLE_NAME_FORMAT % base_name
    script_filename = basename(__file__)

    with open(output_path, "w") as output:
        output.write("#ifndef %s\n" % include_guard)
        output.write("#define %s\n\n" % include_guard)

        output.write("// Generated from \"%s\" using \"%s\".\n" % (
            source_filename, script_filename))
        output.write("const char %s[] =\n" % variable_name)

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
            output.write(line_format % line)
            output.write("\n")

        output.write("\n#endif  // %s\n" % include_guard)


if __name__ == '__main__':
    app.run(main)

from PIL import ImageFont
from PIL.ImageDraw import Draw

# The TrueType or OpenType font file.
FONT_FILE = "assets/SubVario-Condensed-Medium.otf"

# The factor to get text height from text size. Not measured so it works with
# older PIL versions.
TEXT_HEIGHT_FACTOR = 1.2

# Modified widths of characers for better kerning.
CHARACTER_WIDTHS = {
    " ": 5,
    "1": 8
}


def draw_text(text, text_size, text_color, xy=None, box_color=None,
              box_padding=0, border_color=None, border_width=0,
              text_y_offset=0, image=None, draw=None):
    """Draws centered text on an image, optionally in a box."""

    assert image or draw, "Must specify one of image or draw."

    if not draw:
        draw = Draw(image)
    font = ImageFont.truetype(FONT_FILE, size=text_size)

    # Measure the width of each character.
    character_widths = []
    for character in text:
        # Override the measured width, if specified.
        if character in CHARACTER_WIDTHS.keys():
            character_width = CHARACTER_WIDTHS[character]
        else:
            character_width, _ = draw.textsize(character, font)
        character_widths.append(character_width)
    text_width = sum(character_widths)

    # If no xy is specified, center within the image.
    text_height = text_size / TEXT_HEIGHT_FACTOR
    if xy:
        x = xy[0] - text_width // 2
        y = xy[1] - text_height // 2
    else:
        x = image.size[0] // 2 - text_width // 2
        y = image.size[1] // 2 - text_height // 2

    # Draw the box background and border.
    box_xy = [x - box_padding,
              y - box_padding,
              x + text_width + box_padding,
              y + text_height + box_padding]
    border_xy = [box_xy[0] - border_width,
                 box_xy[1] - border_width,
                 box_xy[2] + border_width,
                 box_xy[3] + border_width]
    if border_color:
        draw.rectangle(border_xy, border_color)
    if box_color:
        draw.rectangle(box_xy, box_color)

    # Draw the text character by character.
    y -= text_y_offset
    for index in range(len(text)):
        character = text[index]
        draw.text((x, y), character, text_color, font)
        x += character_widths[index]

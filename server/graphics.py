from PIL import ImageFont
from PIL.ImageDraw import Draw

# The FF SubVario Condensed Medium pixel font.
SUBVARIO_CONDENSED_MEDIUM = {
    "file": "assets/SubVario-Condensed-Medium.otf",
    "size": 24,
    "height": 20,
    "y_offset": 1,
    "width_overrides": {
        " ": 5,
        "1": 8
    }
}

# The FF Screenstar Small Regular pixel font.
SCREENSTAR_SMALL_REGULAR = {
    "file": "assets/Screenstar-Small-Regular.otf",
    "size": 12,
    "height": 10,
    "y_offset": 4,
    "width_overrides": {
        " ": 3
    }
}


def draw_text(text, font_spec, text_color, xy=None, anchor=None,
              box_color=None, box_padding=0, border_color=None, border_width=0,
              image=None):
    """Draws centered text on an image, optionally in a box."""

    draw = Draw(image)
    text_size = font_spec["size"]
    font = ImageFont.truetype(font_spec["file"], size=text_size)

    # Measure the width of each character.
    character_widths = []
    for character in text:
        # Override the measured width, if specified.
        width_overrides = font_spec["width_overrides"]
        if character in width_overrides.keys():
            character_width = width_overrides[character]
        else:
            character_width, _ = draw.textsize(character, font)
        character_widths.append(character_width)
    text_width = sum(character_widths)

    # If no xy is specified, calcuate based on the anchor.
    text_height = font_spec["height"]
    if xy:
        x = xy[0] - text_width // 2
        y = xy[1] - text_height // 2
    elif anchor == "center":
        x = image.width // 2 - text_width // 2
        y = image.height // 2 - text_height // 2
    elif anchor == "bottom_right":
        x = image.width - box_padding - border_width - text_width
        y = image.height - box_padding - border_width - text_height

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
    y -= font_spec["y_offset"]
    for index in range(len(text)):
        character = text[index]
        draw.text((x, y), character, text_color, font)
        x += character_widths[index]

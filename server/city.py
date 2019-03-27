from PIL import Image
from random import uniform

from sun import is_daylight
from weather import is_cloudy


def _random_line(xy1, xy2):
    """Picks a random point along a line."""

    alpha = uniform(0, 1)
    x = xy1[0] + int(alpha * (xy2[0] - xy1[0]))
    y = xy1[1] + int(alpha * (xy2[1] - xy1[1]))
    return (x, y)


# TODO: Replace with final artwork and actual rules.
# The layers making up the city scene. Each layer can define:
# "file": The filename of the image content for this layer.
# "xy": The top left position of this layer.
# "xy_transform": A function that calculates "xy" instead.
# "xy_data": The arguments to "xy_transform" function.
# "condition": A function that determines whether to show this layer.
LAYERS = [
    {
        "file": "city/00-background.gif",
        "xy": (0, 0)
    },
    {
        "file": "city/01-periphery.gif",
        "xy": (0, 0)
    },
    {
        "file": "city/02-car.gif",
        "xy_transform": _random_line,
        "xy_data": [(410, 105), (464, 132)],
        "condition": is_daylight
    },
    {
        "file": "city/03-building.gif",
        "xy": (200, 4)
    },
    {
        "file": "city/04-car.gif",
        "xy_transform": _random_line,
        "xy_data": [(194, 192), (248, 219)],
        "condition": is_daylight
    },
    {
        "file": "city/05-car.gif",
        "xy_transform": _random_line,
        "xy_data": [(436, 152), (300, 220)],
        "condition": is_daylight
    },
    {
        "file": "city/06-car.gif",
        "xy_transform": _random_line,
        "xy_data": [(440, 158), (298, 229)],
        "condition": is_daylight
    },
    {
        "file": "city/07-building.gif",
        "xy": (12, 51)
    },
    {
        "file": "city/08-building.gif",
        "xy": (334, 192)
    },
    {
        "file": "city/09-car.gif",
        "xy_transform": _random_line,
        "xy_data": [(130, 277), (208, 238)],
        "condition": is_daylight
    },
    {
        "file": "city/10-stuff.gif",
        "xy": (70, 196)
    },
    {
        "file": "city/11-guys.gif",
        "xy_transform": _random_line,
        "xy_data": [(209, 294), (289, 334)],
        "condition": is_daylight
    },
    {
        "file": "city/12-clouds.gif",
        "xy": (0, 0),
        "condition": is_cloudy
    }
]


def get_city_image(width, height):
    """Generates an image with a dynamic city scene."""

    image = Image.new(mode="RGB", size=(width, height))

    # Draw the layers in order.
    for layer in LAYERS:
        # Evaluate the optional condition to show this layer.
        try:
            if not layer["condition"]():
                continue
        except KeyError:
            pass

        # Get the coordinates, optinally transforming them first.
        try:
            x, y = layer["xy_transform"](*layer["xy_data"])
        except KeyError:
            x, y = layer["xy"]

        # Draw the layer.
        bitmap = Image.open(layer["file"]).convert("RGBA")
        image.paste(bitmap, (x, y), bitmap)

    return image

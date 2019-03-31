from PIL import Image
from random import choice
from random import uniform

from sun import is_daylight
from weather import is_cloudy


def _random_line(xys):
    """Picks a random point along a line. Expects a list of two tuples."""

    alpha = uniform(0, 1)
    x = xys[0][0] + int(alpha * (xys[1][0] - xys[0][0]))
    y = xys[0][1] + int(alpha * (xys[1][1] - xys[0][1]))
    return (x, y)


# TODO: Replace with final artwork and actual rules.

# The layers making up the city scene. Each layer can define:
# "file": The filename of the image content for this layer.
# "xy": The top left position of this layer.
# "xy_transform": A function that calculates "xy" instead, such as _random_line
#                 or random.choice.
# "xy_data": The arguments to "xy_transform" function.
# "condition": A function that determines whether to show this layer, such as
#              sun.is_daylight or weather.is_cloudy.
LAYERS = [
    {
        "file": "city/PT-water-DYC-01k.gif",
        "xy": (0, 0)
    },
    {
        "file": "city/PT-GroundIsle-DYC-04k.gif",
        "xy": (0, 0)
    },
    {
        "file": "city/PT-facstdo-DYC-02k.gif",
        "xy": (262, 9)
    },
    {
        "file": "city/PT-lightpole-DYC-01k.gif",
        "xy": (130, 5)
    },
    {
        "file": "city/PT-very-little-gravitas-bldg-01k.gif",
        "xy": (188, 18)
    },
    {
        "file": "city/PT-dingdongbldg-DYC-04k.gif",
        "xy": (74, 59)
    },
    {
        "file": "city/PT-van2-DYC-Bus-yp-03k.gif",
        "xy": (156, 116),
        "condition": is_daylight
    },
    {
        "file": "city/PT-streetlight-xp-02k.gif",
        "xy": (314, 11)
    },
    {
        "file": "city/PT-MiniHouseline-03k.gif",
        "xy": (418, 6)
    },
    {
        "file": "city/PT-HomeHouse-DYC-04k.gif",
        "xy": (422, 36)
    },
    {
        "file": "city/PT-sportsboat-DYC-yp-01k.gif",
        "xy": (590, 87)
    },
    {
        "file": "city/PT-blockbobcar-DYC-xp-01k.gif",
        "xy": (418, 109),
        "condition": is_daylight
    },
    {
        "file": "city/PT-robosuper-DYC-day-03k.gif",
        "xy": (540, 116)
    },
    {
        "file": "city/PT-centerblock-DYC-day-08k.gif",
        "xy": (200, 6)
    },
    {
        "file": "city/PT-billboardOne-CoSaNo-02k.gif",
        "xy": (386, 51)
    },
    {
        "file": "city/PT-3-letter-LED-UFO-01k.gif",
        "xy": (354, 125)
    },
    {
        "file": "city/PT-streetlight-yp-02k.gif",
        "xy": (168, 125)
    },
    {
        "file": "city/PT-groupOfRobots-01k.gif",
        "xy": (554, 168)
    },
    {
        "file": "city/PT-streetlight-yp-02k.gif",
        "xy": (516, 119)
    },
    {
        "file": "city/PT-Dyna-Delivery-Biker-xm-01k.gif",
        "xy": (500, 142),
        "condition": is_daylight
    },
    {
        "file": "city/PT-leftblock-DYC-day-11k.gif",
        "xy": (12, 51)
    },
    {
        "file": "city/PT-boatydoaty-DYC-yp-02k.gif",
        "xy": (6, 238)
    },
    {
        "file": "city/PT-bench-DYC-01k.gif",
        "xy": (48, 245)
    },
    {
        "file": "city/PT-small-motorboat-ym-02k.gif",
        "xy": (12, 261)
    },
    {
        "file": "city/PT-streetlight-ym-02k.gif",
        "xy": (38, 224)
    },
    {
        "file": "city/PT-van-DYC-yp-02k.gif",
        "xy": (412, 164),
        "condition": is_daylight
    },
    {
        "file": "city/PT-van2-DYC-Milk-yp-03k.gif",
        "xy": (440, 158),
        "condition": is_daylight
    },
    {
        "file": "city/PT-basevan2-DYC-yp-02k.gif",
        "xy": (388, 184),
        "condition": is_daylight
    },
    {
        "file": "city/PT-sportscar-DYC-xp-02k.gif",
        "xy": (236, 213),
        "condition": is_daylight
    },
    {
        "file": "city/PT-basecar-DYC-y-01k.gif",
        "xy": (152, 266),
        "condition": is_daylight
    },
    {
        "file": "city/PT-block-lilstores-DYC-day-05k.gif",
        "xy": (334, 191)
    },
    {
        "file": "city/PT-cleat-x-01k.gif",
        "xy": (334, 191)
    },
    {
        "file": "city/PT-robotransportboat-xm-02k.gif",
        "xy": (574, 222),
    },
    {
        "file": "city/PT-Jetty-DYC-02k.gif",
        "xy": (516, 230)
    },
    {
        "file": "city/PT-streetlight-yp-02k.gif",
        "xy": (528, 255)
    },
    {
        "file": "city/PT-park-DYC-day-05k.gif",
        "xy": (379, 252)
    },
    {
        "file": "city/PT-Dyna-Bank-with-Dogs-VAR-02k.gif",
        "xy": (496, 312)
    },
    {
        "file": "city/PT-girlwbird-01k.gif",
        "xy": (399, 303),
        "condition": is_daylight
    },
    {
        "file": "city/PT-streetlight-ym-02k.gif",
        "xy": (294, 218)
    },
    {
        "file": "city/PT-block-piershops-DYC-day-02k.gif",
        "xy": (216, 197)
    },
    {
        "file": "city/PT-cleat-y-01k.gif",
        "xy": (400, 346)
    },
    {
        "file": "city/PT-vrguy-A-01k.gif",
        "xy_transform": choice,
        "xy_data": [(217, 298), (237, 308)]
    },
    {
        "file": "city/PT-vrguy-B-01k.gif",
        "xy_transform": choice,
        "xy_data": [(240, 305), (260, 315)]
    },
    {
        "file": "city/PT-HoneyBucket-DYC-02k.gif",
        "xy": (146, 291)
    },
    {
        "file": "city/PT-minicyclops-01k.gif",
        "xy": (40, 291)
    },
    {
        "file": "city/PT-cleat-y-01k.gif",
        "xy": (10, 309)
    },
    {
        "file": "city/PT-cleat-y-01k.gif",
        "xy": (26, 317)
    },
    {
        "file": "city/PT-Cyclops-DYC-04k.gif",
        "xy": (62, 289)
    },
    {
        "file": "city/PT-xachtx-DYC-xm-02k.gif",
        "xy": (544, 302)
    },
    {
        "file": "city/PT-yacht-DYC-xm-03k.gif",
        "xy": (506, 334)
    },
    {
        "file": "city/PT-Dyna-Houseboat-03k.gif",
        "xy": (163, 326)
    },
    {
        "file": "city/PT-streetlight-xp-02k.gif",
        "xy": (216, 322)
    },
    {
        "file": "city/PT-sun-01k.gif",
        "xy": (21, 19)
    },
    {
        "file": "city/PT-cloud-one-01k.gif",
        "xy": (523, 5),
        "condition": is_cloudy
    },
    {
        "file": "city/PT-cloud-two-01k.gif",
        "xy": [-43, 41],
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
            x, y = layer["xy_transform"](layer["xy_data"])
        except KeyError:
            x, y = layer["xy"]

        # Draw the layer.
        bitmap = Image.open(layer["file"]).convert("RGBA")
        image.paste(bitmap, (x, y), bitmap)

    return image

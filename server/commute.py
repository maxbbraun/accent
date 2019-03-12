from google.appengine.api import urlfetch
from json import loads as json_loads
from PIL import Image
from PIL import ImageFont
from PIL.ImageDraw import Draw
from StringIO import StringIO
from urllib import quote

from commute_data import MAPS_API_KEY
from commute_data import HOME_ADDRESS
from commute_data import WORK_ADDRESS
from commute_data import TRAVEL_MODE

# The endpoint of the Static Map API.
STATIC_MAP_URL = "https://maps.googleapis.com/maps/api/staticmap"

# The endpoint of the Directions API.
DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"

# The size of the directions text.
TEXT_SIZE = 24

# The font of the directions text.
FONT = ImageFont.truetype("assets/SubVario-Condensed-Medium.otf",
                          size=TEXT_SIZE)

# The color of the directions text.
TEXT_COLOR = (255, 255, 255)

# The color of the box behind the text.
BOX_COLOR = (0, 0, 0)

# The color of the border around the box.
BORDER_COLOR = (255, 255, 255)

# The width of the border around the box.
BORDER_WIDTH = 3

# The offset used to vertically center the text in the box.
TEXT_OFFSET = 1

# The text height. Not measured to work with older PIL versions.
TEXT_HEIGHT = 20

# The padding of the box around the text.
TEXT_PADDING = 8

# The weight of the directions path.
PATH_WEIGHT = 6


def _get_route_url(api_key, home, work, mode):
    """Constructs the URL for the Directions API request."""

    url = DIRECTIONS_URL
    url += "?key=%s" % api_key
    url += "&origin=%s" % quote(home)
    url += "&destination=%s" % quote(work)
    url += "&mode=%s" % mode
    url += "&departure_time=now"
    return url


def _get_static_map_url(api_key, polyline, width, height):
    """Constructs the URL for the Static Map API request."""

    url = STATIC_MAP_URL
    url += "?key=%s" % api_key
    url += "&size=%dx%d" % (width, height)
    url += "&maptype=roadmap"
    url += "&style=feature:administrative|visibility:off"
    url += "&style=feature:poi|visibility:off"
    url += "&style=feature:all|element:labels|visibility:off"
    url += "&style=feature:landscape|color:0xffffff"
    url += "&style=feature:road|color:0x000000"
    url += "&style=feature:water|color:0x000000"
    url += "&path=color:0xff0000ff|weight:%d|enc:%s" % (PATH_WEIGHT,
                                                        quote(polyline))
    return url


def get_commute_image(width, height):
    """Generates an image with the commute route on a map."""

    # Get the directions from home to work.
    directions_url = _get_route_url(MAPS_API_KEY, HOME_ADDRESS, WORK_ADDRESS,
                                    TRAVEL_MODE)
    directions_response = urlfetch.fetch(directions_url)
    directions = json_loads(directions_response.content)

    # Extract the route polyline, duration, and description.
    route = directions["routes"][0]
    polyline = route["overview_polyline"]["points"]
    summary = route["summary"]
    duration = route["legs"][0]["duration"]["text"]

    # Get the static map as an image.
    image_url = _get_static_map_url(MAPS_API_KEY, polyline, width, height)
    image_response = urlfetch.fetch(image_url)
    image = Image.open(StringIO(image_response.content)).convert("RGB")

    # Draw the directions text inside a centered box.
    draw = Draw(image)
    text = "%s via %s" % (duration, summary)
    text_width, _ = draw.textsize(text, FONT)
    box_xy = [image.size[0] // 2 - text_width // 2 - TEXT_PADDING,
              image.size[1] // 2 - TEXT_HEIGHT // 2 - TEXT_PADDING,
              image.size[0] // 2 + text_width // 2 + TEXT_PADDING,
              image.size[1] // 2 + TEXT_HEIGHT // 2 + TEXT_PADDING]
    border_xy = [box_xy[0] - BORDER_WIDTH, box_xy[1] - BORDER_WIDTH,
                 box_xy[2] + BORDER_WIDTH, box_xy[3] + BORDER_WIDTH]
    draw.rectangle(border_xy, BORDER_COLOR)
    draw.rectangle(box_xy, BOX_COLOR)
    text_xy = (image.size[0] // 2 - text_width // 2,
               image.size[1] // 2 - TEXT_HEIGHT // 2 - TEXT_OFFSET)
    draw.text(text_xy, text, TEXT_COLOR, FONT)

    return image

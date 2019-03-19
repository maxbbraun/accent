from google.appengine.api import urlfetch
from time import mktime
from json import loads as json_loads
from PIL import Image
from pytz import utc
from StringIO import StringIO
from urllib import quote

from commute_data import MAPS_API_KEY
from commute_data import HOME_ADDRESS
from commute_data import WORK_ADDRESS
from commute_data import TRAVEL_MODE
from graphics import draw_text
from graphics import SCREENSTAR_SMALL_REGULAR
from graphics import SUBVARIO_CONDENSED_MEDIUM
from timezone import get_now

# The endpoint of the Static Map API.
STATIC_MAP_URL = "https://maps.googleapis.com/maps/api/staticmap"

# The endpoint of the Directions API.
DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"

# The color of the directions text.
DIRECTIONS_TEXT_COLOR = (255, 255, 255)

# The color of the box behind the directions text.
DIRECTIONS_BOX_COLOR = (0, 0, 0)

# The color of the border around the directions text.
DIRECTIONS_BORDER_COLOR = (255, 255, 255)

# The width of the border around the directions text.
DIRECTIONS_BORDER_WIDTH = 3

# The padding of the box around the directions text.
DIRECTIONS_BOX_PADDING = 8

# The weight of the directions path.
PATH_WEIGHT = 6

# The color of the copyright text.
COPYRIGHT_TEXT_COLOR = (0, 0, 0)

# The color of the box behind the copyright text.
COPYRIGHT_BOX_COLOR = (255, 255, 255)

# The padding of the box around the copyright text.
COPYRIGHT_BOX_PADDING = 2


def _get_route_url(api_key, home, work, mode, timestamp):
    """Constructs the URL for the Directions API request."""

    url = DIRECTIONS_URL
    url += "?key=%s" % api_key
    url += "&origin=%s" % quote(home)
    url += "&destination=%s" % quote(work)
    url += "&mode=%s" % mode
    url += "&departure_time=%d" % timestamp
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
    url += "&style=feature:transit|color:0xffffff"
    url += "&style=feature:transit.line|color:0x000000"
    url += "&style=feature:water|color:0x000000"
    url += "&path=color:0xff0000ff|weight:%d|enc:%s" % (PATH_WEIGHT,
                                                        quote(polyline))
    return url


def get_commute_image(width, height):
    """Generates an image with the commute route on a map."""

    # Use the current time for live traffic.
    now = get_now()
    timestamp = int(mktime(now.astimezone(utc).timetuple()))

    # Get the directions from home to work.
    directions_url = _get_route_url(MAPS_API_KEY, HOME_ADDRESS, WORK_ADDRESS,
                                    TRAVEL_MODE, timestamp)
    directions_response = urlfetch.fetch(directions_url)
    directions = json_loads(directions_response.content)

    # Extract the route polyline, duration, and description.
    route = directions["routes"][0]  # Expect one route.
    polyline = route["overview_polyline"]["points"]
    summary = route["summary"]
    leg = route["legs"][0]  # Expect one leg.
    try:
        duration = leg["duration_in_traffic"]["text"]
    except KeyError:
        duration = leg["duration"]["text"]

    # Get the static map as an image.
    image_url = _get_static_map_url(MAPS_API_KEY, polyline, width, height)
    image_response = urlfetch.fetch(image_url)
    image = Image.open(StringIO(image_response.content)).convert("RGB")

    # Draw the map copyright notice.
    draw_text(u"Map data \xa9%d Google" % now.year,
              font_spec=SCREENSTAR_SMALL_REGULAR,
              text_color=COPYRIGHT_TEXT_COLOR,
              anchor="bottom_right",
              box_color=COPYRIGHT_BOX_COLOR,
              box_padding=COPYRIGHT_BOX_PADDING,
              image=image)

    # Draw the directions text inside a centered box.
    draw_text("%s via %s" % (duration, summary),
              font_spec=SUBVARIO_CONDENSED_MEDIUM,
              text_color=DIRECTIONS_TEXT_COLOR,
              anchor="center",
              box_color=DIRECTIONS_BOX_COLOR,
              box_padding=DIRECTIONS_BOX_PADDING,
              border_color=DIRECTIONS_BORDER_COLOR,
              border_width=DIRECTIONS_BORDER_WIDTH,
              image=image)

    return image

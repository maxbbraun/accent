from google.appengine.api import urlfetch
from json import loads as json_loads
from PIL import Image
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


def _get_route_url(api_key, home, work, mode):
    """Constructs the URL for the Directions API request."""

    url = DIRECTIONS_URL
    url += "?key=%s" % api_key
    url += "&origin=%s" % quote(home)
    url += "&destination=%s" % quote(work)
    url += "&mode=%s" % mode
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
    url += "&path=color:0xff0000ff|weight:5|enc:%s" % quote(polyline)
    return url


def get_commute_image(width, height):
    """Generates an image with the commute route on a map."""

    # Get the directions from home to work and extract the route polyline.
    directions_url = _get_route_url(MAPS_API_KEY, HOME_ADDRESS, WORK_ADDRESS,
                                    TRAVEL_MODE)
    directions_response = urlfetch.fetch(directions_url)
    directions = json_loads(directions_response.content)
    route = directions["routes"][0]
    polyline = route["overview_polyline"]["points"]

    # Get the static map as an image.
    image_url = _get_static_map_url(MAPS_API_KEY, polyline, width, height)
    image_response = urlfetch.fetch(image_url)
    image = Image.open(StringIO(image_response.content)).convert("RGB")

    return image

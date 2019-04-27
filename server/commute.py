from time import mktime
from PIL import Image
from pytz import utc
from requests import get
from io import BytesIO
from urllib.parse import quote

from epd import DISPLAY_WIDTH
from epd import DISPLAY_HEIGHT
from firestore import Firestore
from graphics import draw_text
from graphics import SCREENSTAR_SMALL_REGULAR
from graphics import SUBVARIO_CONDENSED_MEDIUM
from local_time import LocalTime

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


class Commute:
    """The commute route on a map."""

    def __init__(self, user):
        self.local_time = LocalTime(user)
        self.home = user.get("home")
        self.work = user.get("work")
        self.travel_mode = user.get("travel_mode")
        self.google_maps_api_key = Firestore().google_maps_api_key()

    def _route_url(self, timestamp):
        """Constructs the URL for the Directions API request."""

        url = DIRECTIONS_URL
        url += "?key=%s" % self.google_maps_api_key
        url += "&origin=%s" % quote(self.home)
        url += "&destination=%s" % quote(self.work)
        url += "&mode=%s" % self.travel_mode
        url += "&departure_time=%d" % timestamp
        return url

    def _static_map_url(self, polyline, width, height):
        """Constructs the URL for the Static Map API request."""

        url = STATIC_MAP_URL
        url += "?key=%s" % self.google_maps_api_key
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

    def image(self):
        """Generates the current commute image."""

        # Use the current time for live traffic.
        time = self.local_time.now()
        timestamp = int(mktime(time.astimezone(utc).timetuple()))

        # Get the directions from home to work.
        directions_url = self._route_url(timestamp)
        directions = get(directions_url).json()

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
        image_url = self._static_map_url(polyline, DISPLAY_WIDTH,
                                         DISPLAY_HEIGHT)
        image_response = get(image_url).content
        image = Image.open(BytesIO(image_response)).convert("RGB")

        # Draw the map copyright notice.
        copyright_text = u"Map data \xa9%d Google" % time.year
        draw_text(copyright_text,
                  font_spec=SCREENSTAR_SMALL_REGULAR,
                  text_color=COPYRIGHT_TEXT_COLOR,
                  anchor="bottom_right",
                  box_color=COPYRIGHT_BOX_COLOR,
                  box_padding=COPYRIGHT_BOX_PADDING,
                  image=image)

        # Draw the directions text inside a centered box.
        if summary:
            directions_text = "%s via %s" % (duration, summary)
        else:
            directions_text = duration
        draw_text(directions_text,
                  font_spec=SUBVARIO_CONDENSED_MEDIUM,
                  text_color=DIRECTIONS_TEXT_COLOR,
                  anchor="center",
                  box_color=DIRECTIONS_BOX_COLOR,
                  box_padding=DIRECTIONS_BOX_PADDING,
                  border_color=DIRECTIONS_BORDER_COLOR,
                  border_width=DIRECTIONS_BORDER_WIDTH,
                  image=image)

        return image

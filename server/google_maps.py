from cachetools import cached
from cachetools import TTLCache
from google.cloud import vision
from io import BytesIO
from logging import warning
from PIL import Image
from re import compile as re_compile
from requests import get
from requests.exceptions import RequestException
from urllib.parse import quote

from graphics import SCREENSTAR_SMALL_REGULAR
from firestore import DataError
from firestore import Firestore
from graphics import draw_text
from local_time import LocalTime

# The endpoint of the Static Map API.
STATIC_MAP_URL = 'https://maps.googleapis.com/maps/api/staticmap'

# The endpoint of the Directions API.
DIRECTIONS_URL = 'https://maps.googleapis.com/maps/api/directions/json'

# The default map copyright text. The parameter is the current year.
COPYRIGHT_TEXT = 'Map data \xa9%d Google'

# The regular expression pattern identifying the copyright text.
COPYRIGHT_PATTERN = re_compile(r'^.*(Map data.*)$')

# The color of the copyright text.
COPYRIGHT_TEXT_COLOR = (0, 0, 0)

# The color of the box behind the copyright text.
COPYRIGHT_BOX_COLOR = (255, 255, 255)

# The padding of the box around the copyright text.
COPYRIGHT_BOX_PADDING = 3

# The weight of the directions path.
PATH_WEIGHT = 6

# The maximum number of map images kept in the cache.
MAX_CACHE_SIZE = 100

# The time to live in seconds for cached map images.
CACHE_TTL_S = 24 * 60 * 60  # 1 day


class GoogleMaps(object):
    """A wrapper around the Google Static Map and Directions APIs."""

    def __init__(self, geocoder):
        self._google_maps_api_key = Firestore().google_maps_api_key()
        self._local_time = LocalTime(geocoder)
        self._vision_client = vision.ImageAnnotatorClient()

    def _static_map_url(self, size, polyline=None, markers=None, marker_icon=None,
                        hide_map=False):
        """Constructs the URL for the Static Map API request."""

        url = STATIC_MAP_URL
        url += '?key=%s' % self._google_maps_api_key
        url += '&size=%dx%d' % size
        url += '&maptype=roadmap'

        if hide_map:
            url += '&style=all|visibility:off'
        else:
            url += '&style=feature:administrative|visibility:off'
            url += '&style=feature:poi|visibility:off'
            url += '&style=feature:all|element:labels|visibility:off'
            url += '&style=feature:landscape|color:0xffffff'
            url += '&style=feature:road|color:0x000000'
            url += '&style=feature:transit|color:0xffffff'
            url += '&style=feature:transit.line|color:0x000000'
            url += '&style=feature:water|color:0x000000'

        if polyline:
            if hide_map:
                path_color = '0x00000000'
            else:
                path_color = '0xff0000ff'
            url += '&path=color:%s|weight:%d|enc:%s' % (
                path_color, PATH_WEIGHT, quote(polyline))

        if markers:
            # Use the specified marker icon or a default style.
            if marker_icon:
                style = 'anchor:center|icon:%s' % quote(marker_icon)
            else:
                style = 'size:tiny|color:0xff0000ff'
            url += '&markers=%s|%s' % (style, quote(markers))

        return url

    def _download_map(self, size, polyline=None, markers=None, marker_icon=None,
                      hide_map=False):
        """Downloads the image data from the Google Static Map API."""

        image_url = self._static_map_url(size,
                                         polyline=polyline, markers=markers,
                                         marker_icon=marker_icon,
                                         hide_map=hide_map)

        try:
            image_response = get(image_url).content
        except RequestException as e:
            raise DataError(e)
        image_data = BytesIO(image_response)

        return image_data

    def _copyright_text(self, size, polyline=None, markers=None, marker_icon=None):
        """Uses OCR to extract the copyright text from the map."""

        # Download a version of the map with only the copyright text.
        image_data = self._download_map(size, 
                                        polyline=polyline, markers=markers,
                                        marker_icon=marker_icon,
                                        hide_map=True)

        # Make a request to the Vision API.
        request_image = vision.types.Image(content=image_data.getvalue())
        response = self._vision_client.document_text_detection(
            image=request_image)

        # Parse all recognized text for the copyright.
        lines = response.full_text_annotation.text.splitlines()
        for line in lines:
            matches = COPYRIGHT_PATTERN.match(line)
            if matches:
                return matches.group(1)

        warning('Falling back to default copyright text.')
        time = self._local_time.utc_now()
        return COPYRIGHT_TEXT % time.year

    @cached(cache=TTLCache(maxsize=MAX_CACHE_SIZE, ttl=CACHE_TTL_S))
    def map_image(self, size, polyline=None, markers=None, marker_icon=None):
        """Creates a map image with optional route or markers."""

        scaled_width = size[0]
        scaled_height = size[1]

        # Google Static Maps is limited to 640x640
        # Limit image to this size, and resize at the end
        if size[0] > 640:
            scaled_width = 640
            scaled_height = 640 * (size[1] / size[0])

        # Get the static map as an image.
        image_data = self._download_map(size=(scaled_width, scaled_height), 
                                        polyline=polyline, markers=markers,
                                        marker_icon=marker_icon)
        image = Image.open(image_data).convert('RGB')

        # Replace the copyright text with a more readable pixel font.
        copyright_text = self._copyright_text(size=(scaled_width, scaled_height), 
                                              polyline=polyline,
                                              markers=markers,
                                              marker_icon=marker_icon)

        scaled_font_spec = SCREENSTAR_SMALL_REGULAR.copy()
        if scaled_width != size[0]:
            scaled_font_spec['size'] *= 2
            scaled_font_spec['height'] *= 2
            image = image.resize(size)

        draw_text(copyright_text,
                  font_spec=scaled_font_spec,
                  text_color=COPYRIGHT_TEXT_COLOR,
                  anchor='bottom_right',
                  box_color=COPYRIGHT_BOX_COLOR,
                  box_padding=COPYRIGHT_BOX_PADDING,
                  image=image)

        return image

    def _route_url(self, home, work, travel_mode):
        """Constructs the URL for the Directions API request."""

        if not home:
            raise DataError('Missing home address')

        if not work:
            raise DataError('Missing work address')

        if not travel_mode:
            raise DataError('Missing travel mode')

        url = DIRECTIONS_URL
        url += '?key=%s' % self._google_maps_api_key
        url += '&origin=%s' % quote(home)
        url += '&destination=%s' % quote(work)
        url += '&mode=%s' % travel_mode
        url += '&departure_time=now'

        return url

    def directions(self, user):
        """Gets the directions from the user's home to work."""

        # Get the user's addresses.
        try:
            home = user.get('home')
            work = user.get('work')
            travel_mode = user.get('travel_mode')
        except KeyError as e:
            raise DataError(e)

        # Make the Directions API request.
        directions_url = self._route_url(home, work, travel_mode)
        directions = get(directions_url).json()

        return directions

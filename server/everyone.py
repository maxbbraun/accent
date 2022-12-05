from astral import AstralError
from cachetools import cached
from cachetools import TTLCache
from content import ContentError
from content import ImageContent
from firestore import DataError
from firestore import Firestore
from google_maps import GoogleMaps

# The URL of the image used as a marker icon.
MARKER_ICON_URL = 'http://accent.ink/marker.png'

# The time to live in seconds for cached markers.
CACHE_TTL_S = 24 * 60 * 60  # 1 day


class Everyone(ImageContent):
    """A map of Accent users around the world."""

    def __init__(self, geocoder):
        self._geocoder = geocoder
        self._google_maps = GoogleMaps(geocoder)
        self._firestore = Firestore()

    @cached(cache=TTLCache(maxsize=1, ttl=CACHE_TTL_S))
    def _markers(self):
        """Returns a list of users' home locations to be shown on a map."""

        markers = ''

        for user in self._firestore.users():
            try:
                home = user.get('home')
                location = self._geocoder[home]

                # Use the latitude and longitude of the city name and region
                # instead of the exact coordinates to anonymize user addresses.
                city = '%s, %s' % (location.name, location.region)
                anonymized = self._geocoder[city]

                markers += '|%f,%f' % (anonymized.latitude,
                                       anonymized.longitude)
            except (KeyError, AstralError):
                # Skip users with address errors.
                pass

        return markers

    def image(self, user, width, height, variant):
        """Generates a map with user locations."""

        try:
            return self._google_maps.map_image(width, height, variant,
                                               markers=self._markers(),
                                               marker_icon=MARKER_ICON_URL)
        except DataError as e:
            raise ContentError(e)

from cachetools import cached
from cachetools import TTLCache
from dataclasses import dataclass
from requests import get
from requests.exceptions import RequestException
from time import time

from firestore import DataError
from firestore import Firestore

# The endpoint of the Google Geocoding API.
GEOCODING_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

# The endpoint of the Google Time Zone API.
TIMEZONE_URL = 'https://maps.googleapis.com/maps/api/timezone/json'

# The endpoint of the Google Elevation API.
ELEVATION_URL = 'https://maps.googleapis.com/maps/api/elevation/json'

# The maximum number of locations kept in the cache.
MAX_CACHE_SIZE = 100

# The time to live in seconds for cached locations.
CACHE_TTL_S = 24 * 60 * 60  # 1 day

# The timeout for Google Maps API requests.
REQUEST_TIMEOUT_S = 10


@dataclass(frozen=True)
class Location(object):
    """A geocoded location with the fields used by the server."""

    name: str
    region: str
    latitude: float
    longitude: float
    timezone: str
    elevation: int
    url: str


class Geocoder(object):
    """A Google Maps geocoder with a TTLCache."""

    def __init__(self):
        self._google_maps_api_key = Firestore().google_maps_api_key()

    @cached(cache=TTLCache(maxsize=MAX_CACHE_SIZE, ttl=CACHE_TTL_S))
    def __getitem__(self, key):
        name, region, latitude, longitude = self._geocoding(key)
        timezone = self._timezone(latitude, longitude)
        elevation = self._elevation(latitude, longitude)
        url = 'https://maps.google.com/maps?q=loc:%f,%f' % (
            latitude, longitude)

        return Location(name=name,
                        region=region,
                        latitude=latitude,
                        longitude=longitude,
                        timezone=timezone,
                        elevation=elevation,
                        url=url)

    def _request_json(self, url, params):
        """Requests JSON from a Google Maps API endpoint."""

        params['key'] = self._google_maps_api_key
        try:
            response = get(url, params=params, timeout=REQUEST_TIMEOUT_S)
            response.raise_for_status()
            return response.json()
        except (RequestException, ValueError) as e:
            raise DataError(e)

    def _geocoding(self, key):
        """Looks up coordinates for an address."""

        response = self._request_json(GEOCODING_URL, {'address': key})
        status = response.get('status')
        if status != 'OK':
            raise DataError(
                'Google Geocoding API could not locate %s: %s' % (
                    key, status))

        try:
            result = response['results'][0]
            formatted_address = result['formatted_address']
            location = result['geometry']['location']
            latitude = float(location['lat'])
            longitude = float(location['lng'])
        except (KeyError, IndexError, TypeError, ValueError) as e:
            raise DataError(e)

        separator = formatted_address.find(',')
        if separator == -1:
            name = formatted_address
            region = ''
        else:
            name = formatted_address[:separator].strip()
            region = formatted_address[separator + 1:].strip()

        return name, region, latitude, longitude

    def _timezone(self, latitude, longitude):
        """Looks up the timezone for coordinates."""

        params = {
            'location': '%f,%f' % (latitude, longitude),
            'timestamp': int(time())}
        response = self._request_json(TIMEZONE_URL, params)
        try:
            if response['status'] == 'OK':
                return response['timeZoneId']
        except KeyError as e:
            raise DataError(e)

        return 'UTC'

    def _elevation(self, latitude, longitude):
        """Looks up elevation for coordinates."""

        params = {'locations': '%f,%f' % (latitude, longitude)}
        response = self._request_json(ELEVATION_URL, params)
        try:
            if response['status'] == 'OK':
                return int(float(response['results'][0]['elevation']))
        except (KeyError, IndexError, TypeError, ValueError) as e:
            raise DataError(e)

        return 0

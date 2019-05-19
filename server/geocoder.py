from astral import GoogleGeocoder
from cachetools import cached
from cachetools import TTLCache

from firestore import Firestore

# The maximum number of locations kept in the cache.
MAX_CACHE_SIZE = 100

# The time to live in seconds for cached locations.
CACHE_TTL_S = 24 * 60 * 60  # 1 day


class Geocoder(GoogleGeocoder):
    """A version of astral.GoogleGeocoder with a TTLCache."""

    def __init__(self):
        google_maps_api_key = Firestore().google_maps_api_key()
        GoogleGeocoder.__init__(self, api_key=google_maps_api_key, cache=False)

    @cached(cache=TTLCache(maxsize=MAX_CACHE_SIZE, ttl=CACHE_TTL_S))
    def __getitem__(self, key):
        return GoogleGeocoder.__getitem__(self, key)


class GeocoderWrapper(object):
    """A class to wrap a Geocoder instance and feed it to astral.Astral."""

    def __init__(self, wrapped):
        self.geocoder = wrapped

    def __getitem__(self, key):
        return self.geocoder.__getitem__(key)

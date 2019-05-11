from cachetools import cached
from cachetools import TTLCache
from logging import info
from requests import get

from firestore import Firestore

# The endpoint of the Forecast API.
FORECAST_URL = 'https://api.darksky.net/forecast/%s/%f,%f'

# The maximum number of forecasts kept in the cache.
MAX_CACHE_SIZE = 100

# The time to live in seconds for cached forecasts.
CACHE_TTL_S = 60 * 60  # 1 hour


class Weather(object):
    """A wrapper around the Dark Sky API with a cache."""

    def __init__(self, geocoder):
        self.dark_sky_api_key = Firestore().dark_sky_api_key()
        self.geocoder = geocoder

    def _icon(self, user):
        """Gets the current weather icon for the user's home address."""

        location = self._home_location(user)
        icon = self._request_icon(location)

        return icon

    def _home_location(self, user):
        """Gets the location of the user's home address."""

        home = user.get('home')
        location = self.geocoder[home]

        return location

    @cached(cache=TTLCache(maxsize=MAX_CACHE_SIZE, ttl=CACHE_TTL_S))
    def _request_icon(self, location):
        """Requests the current weather icon from the Dark Sky API."""

        # Look up the weather forecast at the location.
        forecast_url = FORECAST_URL % (self.dark_sky_api_key,
                                       location.latitude,
                                       location.longitude)
        forecast = get(forecast_url).json()

        # Get the icon encoding the current weather.
        icon = forecast['currently']['icon']
        info('Weather: %s' % icon)

        return icon

    def is_clear(self, user):
        """Checks if the current weather is clear."""

        return self._icon(user) in ['clear-day', 'clear-night']

    def is_cloudy(self, user):
        """Checks if the current weather is cloudy."""

        return self._icon(user) == 'cloudy'

    def is_partly_cloudy(self, user):
        """Checks if the current weather is partly cloudy."""

        return self._icon(user) in ['partly-cloudy-day', 'partly-cloudy-night']

    def is_rainy(self, user):
        """Checks if the current weather is rainy."""

        return self._icon(user) in ['rain', 'sleet']

    def is_windy(self, user):
        """Checks if the current weather is windy."""

        return self._icon(user) == 'wind'

    def is_snowy(self, user):
        """Checks if the current weather is snowy."""

        return self._icon(user) == 'snow'

    def is_foggy(self, user):
        """Checks if the current weather is foggy."""

        return self._icon(user) == 'fog'

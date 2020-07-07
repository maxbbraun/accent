from astral import AstralError
from cachetools import cached
from cachetools import TTLCache
from json.decoder import JSONDecodeError
from logging import info
from requests import get
from requests import RequestException

from firestore import DataError
from firestore import Firestore

# The endpoint of the OpenWeather One Call API.
# Spec: https://openweathermap.org/api/one-call-api
OPEN_WEATHER_URL = ('https://api.openweathermap.org/data/2.5/onecall'
                    '?lat=%f&lon=%f&exclude=minutely,hourly,daily&appid=%s')

# The maximum number of weather icons kept in the cache.
MAX_CACHE_SIZE = 100

# The time to live in seconds for cached weather icons.
CACHE_TTL_S = 60 * 60  # 1 hour


class Weather(object):
    """A wrapper around the OpenWeather One Call API with a cache."""

    def __init__(self, geocoder):
        self.open_weather_api_key = Firestore().open_weather_api_key()
        self.geocoder = geocoder

    def _icon(self, user):
        """Gets the current weather icon for the user's home address."""

        location = self._home_location(user)
        return self._request_icon(location)

    def _home_location(self, user):
        """Gets the location of the user's home address."""

        try:
            home = user.get('home')
            return self.geocoder[home]
        except (AstralError, KeyError) as e:
            raise DataError(e)

    @cached(cache=TTLCache(maxsize=MAX_CACHE_SIZE, ttl=CACHE_TTL_S))
    def _request_icon(self, location):
        """Requests the current weather icon from the OpenWeather API."""

        # Look up the current weather conditions at the location.
        request_url = OPEN_WEATHER_URL % (location.latitude,
                                          location.longitude,
                                          self.open_weather_api_key)

        try:
            response_json = get(request_url).json()
            icon = response_json['current']['weather'][0]['icon']
        except (RequestException, JSONDecodeError, KeyError) as e:
            raise DataError(e)

        info('Weather: %s' % icon)
        return icon

    def is_clear(self, user):
        """Checks if the current weather is clear."""

        return self._icon(user) in ['01d', '01n']

    def is_partly_cloudy(self, user):
        """Checks if the current weather is partly cloudy."""

        return self._icon(user) in ['02d', '02n']

    def is_cloudy(self, user):
        """Checks if the current weather is cloudy."""

        return self._icon(user) in ['03d', '03n', '04d', '04n']

    def is_rainy(self, user):
        """Checks if the current weather is rainy."""

        return self._icon(user) in ['09d', '09n', '10d', '10n', '11d', '11n']

    def is_snowy(self, user):
        """Checks if the current weather is snowy."""

        return self._icon(user) in ['13d', '13n']

    def is_foggy(self, user):
        """Checks if the current weather is foggy."""

        return self._icon(user) in ['50d', '50n']

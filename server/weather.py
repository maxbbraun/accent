from astral import AstralError
from cachetools import cached
from cachetools import TTLCache
from json.decoder import JSONDecodeError
from logging import info
from requests import get
from requests import RequestException

from firestore import DataError
from firestore import Firestore

# The base URL for AccuWeather API endpoints.
BASE_URL = 'https://dataservice.accuweather.com'

# The endpoint of the AccuWeather Current Conditions API.
CURRENT_CONDITIONS_URL = '%s/currentconditions/v1/%s?apikey=%s'

# The endpoint of the AccuWeather Geoposition API.
GEOPOSITION_URL = '%s/locations/v1/cities/geoposition/search?apikey=%s&q=%f,%f'

# The maximum number of location keys kept in the cache.
LOCATION_KEY_CACHE_SIZE = 100

# The time to live in seconds for cached location keys.
LOCATION_KEY_CACHE_TTL_S = 24 * 60 * 60  # 1 day

# The maximum number of weather icons kept in the cache.
WEATHER_ICON_CACHE_SIZE = 100

# The time to live in seconds for cached weather icons.
WEATHER_ICON_CACHE_TTL_S = 60 * 60  # 1 hour


class Weather(object):
    """A wrapper around the AccuWeather Current Conditions API with a cache."""

    def __init__(self, geocoder):
        self.accu_weather_api_key = Firestore().accu_weather_api_key()
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

    @cached(cache=TTLCache(maxsize=WEATHER_ICON_CACHE_SIZE,
                           ttl=WEATHER_ICON_CACHE_TTL_S))
    def _request_icon(self, location):
        """Requests the current weather icon from the AccuWeather API."""

        # Look up the current weather conditions at the location.
        location_key = self._request_location_key(location)
        current_conditions_url = CURRENT_CONDITIONS_URL % (
            BASE_URL, location_key, self.accu_weather_api_key)

        try:
            current_conditions = get(current_conditions_url).json()
            icon = current_conditions[0]['WeatherIcon']
        except (RequestException, JSONDecodeError, KeyError) as e:
            raise DataError(e)

        info('Weather: %s' % icon)
        return icon

    @cached(cache=TTLCache(maxsize=LOCATION_KEY_CACHE_SIZE,
                           ttl=LOCATION_KEY_CACHE_TTL_S))
    def _request_location_key(self, location):
        """Requests the location key for the specified location."""

        geoposition_url = GEOPOSITION_URL % (BASE_URL,
                                             self.accu_weather_api_key,
                                             location.latitude,
                                             location.longitude)
        try:
            geoposition = get(geoposition_url).json()
            location_key = geoposition['Key']
        except (RequestException, JSONDecodeError, KeyError) as e:
            raise DataError(e)

        info('Location key: %s' % location_key)
        return location_key

    def is_clear(self, user):
        """Checks if the current weather is clear."""

        return self._icon(user) in [1, 2, 33, 34]

    def is_cloudy(self, user):
        """Checks if the current weather is cloudy."""

        return self._icon(user) in [6, 7, 8]

    def is_partly_cloudy(self, user):
        """Checks if the current weather is partly cloudy."""

        return self._icon(user) in [3, 4, 5, 35, 36, 37, 38]

    def is_rainy(self, user):
        """Checks if the current weather is rainy."""

        return self._icon(user) in [12, 13, 14, 15, 16, 17, 18, 24, 25, 26, 29,
                                    39, 40, 41, 42]

    def is_windy(self, user):
        """Checks if the current weather is windy."""

        return self._icon(user) in [32]

    def is_snowy(self, user):
        """Checks if the current weather is snowy."""

        return self._icon(user) in [19, 23, 43, 44]

    def is_foggy(self, user):
        """Checks if the current weather is foggy."""

        return self._icon(user) in [11]

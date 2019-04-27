from cachetools import cached
from cachetools import TTLCache
from logging import info
from logging import error
from requests import get
from urllib.parse import quote

from firestore import Firestore

# The endpoint of the Geocoding API.
GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"

# The endpoint of the Forecast API.
FORECAST_URL = "https://api.darksky.net/forecast/%s/%f,%f"


class Weather:
    """A wrapper around the Dark Sky API."""

    def __init__(self, user):
        self.home = user.get("home")
        firestore = Firestore()
        self.google_maps_api_key = firestore.google_maps_api_key()
        self.dark_sky_api_key = firestore.dark_sky_api_key()

    @cached(cache=TTLCache(maxsize=1, ttl=300))  # Cache for 5 minutes.
    def _current_icon(self):
        """Gets the current weather icon from the Dark Sky API."""

        # Look up the latitude and longitude of the weather address.
        geocoding_url = GEOCODING_URL
        geocoding_url += "?key=%s" % self.google_maps_api_key
        geocoding_url += "&address=%s" % quote(self.home)
        geocoding = get(geocoding_url).json()

        if geocoding["status"] != "OK":
            error(geocoding["error_message"])
            return ""

        result = geocoding["results"][0]  # Expect one result.
        location = result["geometry"]["location"]
        latitude = float(location["lat"])
        longitude = float(location["lng"])

        # Look up the weather forecast.
        forecast_url = FORECAST_URL % (self.dark_sky_api_key, latitude,
                                       longitude)
        forecast = get(forecast_url).json()

        # Get the icon encoding the current weather.
        icon = forecast["currently"]["icon"]
        info("Weather: %s" % icon)

        return icon

    def is_clear(self):
        """Checks if the current weather is clear."""

        icon = self._current_icon()
        return icon in ["clear-day", "clear-night"]

    def is_cloudy(self):
        """Checks if the current weather is cloudy."""

        icon = self._current_icon()
        return icon == "cloudy"

    def is_partly_cloudy(self):
        """Checks if the current weather is partly cloudy."""

        icon = self._current_icon()
        return icon in ["partly-cloudy-day", "partly-cloudy-night"]

    def is_rainy(self):
        """Checks if the current weather is rainy."""

        icon = self._current_icon()
        return icon in ["rain", "sleet"]

    def is_windy(self):
        """Checks if the current weather is windy."""

        icon = self._current_icon()
        return icon == "wind"

    def is_snowy(self):
        """Checks if the current weather is snowy."""

        icon = self._current_icon()
        return icon == "snow"

    def is_foggy(self):
        """Checks if the current weather is foggy."""

        icon = self._current_icon()
        return icon == "fog"

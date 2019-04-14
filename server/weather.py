from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from cachetools import cached
from cachetools import TTLCache
from google.appengine.api import urlfetch
from json import loads as json_loads
from logging import info
from logging import error
from urllib import quote

from user_data import DARK_SKY_API_KEY
from user_data import HOME_ADDRESS
from user_data import MAPS_API_KEY

# The endpoint of the Geocoding API.
GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"

# The endpoint of the Forecast API.
FORECAST_URL = "https://api.darksky.net/forecast/%s/%f,%f"


@cached(cache=TTLCache(maxsize=1, ttl=3600))  # Cache for 1 hour.
def _current_icon():
    """Gets the current weather icon from the Dark Sky API."""

    # Look up the latitude and longitude of the weather address.
    geocoding_url = GEOCODING_URL
    geocoding_url += "?key=%s" % MAPS_API_KEY
    geocoding_url += "&address=%s" % quote(HOME_ADDRESS)
    geocoding_response = urlfetch.fetch(geocoding_url)
    geocoding = json_loads(geocoding_response.content)

    if geocoding["status"] != "OK":
        error(geocoding["error_message"])
        return ""

    result = geocoding["results"][0]  # Expect one result.
    location = result["geometry"]["location"]
    latitude = float(location["lat"])
    longitude = float(location["lng"])

    # Look up the weather forecast.
    forecast_url = FORECAST_URL % (DARK_SKY_API_KEY, latitude, longitude)
    forecast_response = urlfetch.fetch(forecast_url)
    forecast = json_loads(forecast_response.content)

    # Get the icon encoding the current weather.
    icon = forecast["currently"]["icon"]
    info("Weather: %s" % icon)

    return icon


def is_clear():
    """Checks if the current weather is clear."""

    icon = _current_icon()
    return icon in ["clear-day", "clear-night"]


def is_cloudy():
    """Checks if the current weather is cloudy."""

    icon = _current_icon()
    return icon == "cloudy"


def is_partly_cloudy():
    """Checks if the current weather is partly cloudy."""

    icon = _current_icon()
    return icon in ["partly-cloudy-day", "partly-cloudy-night"]


def is_rainy():
    """Checks if the current weather is rainy."""

    icon = _current_icon()
    return icon in ["rain", "sleet"]


def is_windy():
    """Checks if the current weather is windy."""

    icon = _current_icon()
    return icon == "wind"


def is_snowy():
    """Checks if the current weather is snowy."""

    icon = _current_icon()
    return icon == "snow"


def is_foggy():
    """Checks if the current weather is foggy."""

    icon = _current_icon()
    return icon == "fog"

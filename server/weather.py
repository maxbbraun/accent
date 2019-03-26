from google.appengine.api import urlfetch
from json import loads as json_loads
from logging import debug
from logging import error
from urllib import quote

from user_data import DARK_SKY_API_KEY
from user_data import HOME_ADDRESS
from user_data import MAPS_API_KEY

# The endpoint of the Geocoding API.
GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"

# The endpoint of the Forecast API.
FORECAST_URL = "https://api.darksky.net/forecast/%s/%f,%f"


def _get_daily_icon():
    """Gets today's weather from the Dark Sky API."""

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

    # Get the icon encoding today's weather.
    icon = forecast["daily"]["icon"]
    debug("Weather: %s" % icon)

    return icon


def is_cloudy():
    """Checks if today's weather is cloudy."""

    icon = _get_daily_icon()
    return icon in ["cloudy", "partly-cloudy-day", "partly-cloudy-night"]


def is_rainy():
    """Checks if today's weather is rainy."""

    icon = _get_daily_icon()
    return icon in ["rain", "sleet"]


def is_windy():
    """Checks if today's weather is windy."""

    icon = _get_daily_icon()
    return icon == "wind"


def is_snowy():
    """Checks if today's weather is snowy."""

    icon = _get_daily_icon()
    return icon == "snow"


def is_foggy():
    """Checks if today's weather is foggy."""

    icon = _get_daily_icon()
    return icon == "fog"

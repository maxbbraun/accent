from astral import Astral
from astral import GoogleGeocoder
from croniter import croniter
from datetime import datetime
from datetime import timedelta
from logging import info

from now import now
from user_data import HOME_ADDRESS
from user_data import MAPS_API_KEY
from user_data import TIMEZONE

# A reference to a calculator for sunrise and sunset times.
ASTRAL = Astral(geocoder=GoogleGeocoder, api_key=MAPS_API_KEY)[HOME_ADDRESS]


def rewrite_cron(cron, after):
    """Replaces references to sunrise and sunset in a cron expression."""

    # Skip if there is nothing to rewrite.
    if "sunrise" not in cron and "sunset" not in cron:
        return cron

    # Determine the first two days of the cron expression after the reference,
    # which covers all candidate sunrises and sunsets.
    yesterday = after - timedelta(days=1)
    midnight_cron = cron.replace("sunrise", "0 0").replace("sunset", "0 0")
    first_day = croniter(midnight_cron, yesterday).get_next(datetime)
    second_day = croniter(midnight_cron, first_day).get_next(datetime)

    # Calculate the closest future sunrise time and replace the term in the
    # cron expression with minutes and hours.
    if "sunrise" in cron:
        sunrises = map(lambda x: ASTRAL.sunrise(x).astimezone(TIMEZONE),
                       [first_day, second_day])
        next_sunrise = min(filter(lambda x: x >= after, sunrises))
        sunrise_cron = cron.replace("sunrise", "%d %d" % (next_sunrise.minute,
                                                          next_sunrise.hour))
        info("Rewrote cron: (%s) -> (%s), after %s" % (
             cron,
             sunrise_cron,
             after.strftime("%A %B %d %Y %H:%M:%S %Z")))
        return sunrise_cron

    # Calculate the closest future sunset time and replace the term in the cron
    # expression with minutes and hours.
    if "sunset" in cron:
        sunsets = map(lambda x: ASTRAL.sunset(x).astimezone(TIMEZONE),
                      [first_day, second_day])
        next_sunset = min(filter(lambda x: x >= after, sunsets))
        sunset_cron = cron.replace("sunset", "%d %d" % (next_sunset.minute,
                                                        next_sunset.hour))
        info("Rewrote cron: (%s) -> (%s), after %s" % (
             cron,
             sunset_cron,
             after.strftime("%A %B %d %Y %H:%M:%S %Z")))
        return sunset_cron


def is_daylight():
    """Calculates whether the sun is currently up."""

    # Find the sunrise and sunset times for today.
    time = now()
    sunrise = ASTRAL.sunrise(time).astimezone(TIMEZONE)
    sunset = ASTRAL.sunset(time).astimezone(TIMEZONE)

    is_daylight = time > sunrise and time < sunset

    info("Daylight: %s (%s)" % (is_daylight,
                                time.strftime("%A %B %d %Y %H:%M:%S %Z")))

    return is_daylight

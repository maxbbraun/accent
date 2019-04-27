from astral import Astral
from astral import GoogleGeocoder
from croniter import croniter
from datetime import datetime
from datetime import timedelta
from logging import info

from firestore import Firestore
from local_time import LocalTime


class Sun:
    """A wrapper around a calculator for sunrise and sunset times."""

    def __init__(self, user):
        google_maps_api_key = Firestore().google_maps_api_key()
        home = user.get("home")
        self.astral = Astral(geocoder=GoogleGeocoder,
                             api_key=google_maps_api_key)[home]
        self.local_time = LocalTime(user)

    def rewrite_cron(self, cron, after):
        """Replaces references to sunrise and sunset in a cron expression."""

        # Skip if there is nothing to rewrite.
        if "sunrise" not in cron and "sunset" not in cron:
            return cron

        # Determine the first two days of the cron expression after the
        # reference, which covers all candidate sunrises and sunsets.
        yesterday = after - timedelta(days=1)
        midnight_cron = cron.replace("sunrise", "0 0").replace("sunset", "0 0")
        first_day = croniter(midnight_cron, yesterday).get_next(datetime)
        second_day = croniter(midnight_cron, first_day).get_next(datetime)

        zone = self.local_time.zone()

        # Calculate the closest future sunrise time and replace the term in the
        # cron expression with minutes and hours.
        if "sunrise" in cron:
            sunrises = map(lambda x: self.astral.sunrise(x).astimezone(zone),
                           [first_day, second_day])
            next_sunrise = min(filter(lambda x: x >= after, sunrises))
            sunrise_cron = cron.replace("sunrise", "%d %d" % (
                next_sunrise.minute, next_sunrise.hour))
            info("Rewrote cron: (%s) -> (%s), after %s" % (
                cron,
                sunrise_cron,
                after.strftime("%A %B %d %Y %H:%M:%S %Z")))
            return sunrise_cron

        # Calculate the closest future sunset time and replace the term in the
        # cron expression with minutes and hours.
        if "sunset" in cron:
            sunsets = map(lambda x: self.astral.sunset(x).astimezone(zone),
                          [first_day, second_day])
            next_sunset = min(filter(lambda x: x >= after, sunsets))
            sunset_cron = cron.replace("sunset", "%d %d" % (next_sunset.minute,
                                                            next_sunset.hour))
            info("Rewrote cron: (%s) -> (%s), after %s" % (
                cron,
                sunset_cron,
                after.strftime("%A %B %d %Y %H:%M:%S %Z")))
            return sunset_cron

    def is_daylight(self):
        """Calculates whether the sun is currently up."""

        # Find the sunrise and sunset times for today.
        time = self.local_time.now()
        zone = self.local_time.zone()
        sunrise = self.astral.sunrise(time).astimezone(zone)
        sunset = self.astral.sunset(time).astimezone(zone)

        is_daylight = time > sunrise and time < sunset

        info("Daylight: %s (%s)" % (is_daylight,
                                    time.strftime("%A %B %d %Y %H:%M:%S %Z")))

        return is_daylight

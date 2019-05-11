from astral import Astral
from croniter import croniter
from datetime import datetime
from datetime import timedelta
from logging import info

from geocoder import GeocoderWrapper
from local_time import LocalTime


class Sun:
    """A wrapper around a calculator for sunrise and sunset times."""

    def __init__(self, geocoder):
        self.astral = Astral(geocoder=GeocoderWrapper, wrapped=geocoder)
        self.local_time = LocalTime()

    def _sunrise(self, time, user):
        """Calculates the sunrise time at the user's home address."""

        home = user.get('home')
        return self.astral[home].sunrise(time)

    def _sunset(self, time, user):
        """Calculates the sunset time at the user's home address."""

        home = user.get('home')
        return self.astral[home].sunset(time)

    def rewrite_cron(self, cron, after, user):
        """Replaces references to sunrise and sunset in a cron expression."""

        # Skip if there is nothing to rewrite.
        if 'sunrise' not in cron and 'sunset' not in cron:
            return cron

        # Determine the first two days of the cron expression after the
        # reference, which covers all candidate sunrises and sunsets.
        yesterday = after - timedelta(days=1)
        midnight_cron = cron.replace('sunrise', '0 0').replace('sunset', '0 0')
        first_day = croniter(midnight_cron, yesterday).get_next(datetime)
        second_day = croniter(midnight_cron, first_day).get_next(datetime)

        zone = self.local_time.zone(user)

        # Calculate the closest future sunrise time and replace the term in the
        # cron expression with minutes and hours.
        if 'sunrise' in cron:
            sunrises = map(lambda x: self._sunrise(x, user).astimezone(zone),
                           [first_day, second_day])
            next_sunrise = min(filter(lambda x: x >= after, sunrises))
            sunrise_cron = cron.replace('sunrise', '%d %d' % (
                next_sunrise.minute, next_sunrise.hour))
            info('Rewrote cron: (%s) -> (%s), after %s' % (
                cron,
                sunrise_cron,
                after.strftime('%A %B %d %Y %H:%M:%S %Z')))
            return sunrise_cron

        # Calculate the closest future sunset time and replace the term in the
        # cron expression with minutes and hours.
        if 'sunset' in cron:
            sunsets = map(lambda x: self._sunset(x, user).astimezone(zone),
                          [first_day, second_day])
            next_sunset = min(filter(lambda x: x >= after, sunsets))
            sunset_cron = cron.replace('sunset', '%d %d' % (next_sunset.minute,
                                                            next_sunset.hour))
            info('Rewrote cron: (%s) -> (%s), after %s' % (
                cron,
                sunset_cron,
                after.strftime('%A %B %d %Y %H:%M:%S %Z')))
            return sunset_cron

    def is_daylight(self, user):
        """Calculates whether the sun is currently up."""

        # Find the sunrise and sunset times for today.
        time = self.local_time.now(user)
        zone = self.local_time.zone(user)
        sunrise = self._sunrise(time, user).astimezone(zone)
        sunset = self._sunset(time, user).astimezone(zone)

        is_daylight = time > sunrise and time < sunset

        info('Daylight: %s (%s)' % (is_daylight,
                                    time.strftime('%A %B %d %Y %H:%M:%S %Z')))

        return is_daylight

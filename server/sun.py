from astral import Observer
from astral.sun import sunrise
from astral.sun import sunset
from croniter import croniter
from datetime import datetime
from datetime import timedelta
from logging import info

from firestore import DataError
from local_time import LocalTime


class Sun(object):
    """A wrapper around a calculator for sunrise and sunset times."""

    def __init__(self, geocoder):
        self._geocoder = geocoder
        self._local_time = LocalTime(geocoder)

    def _home_location(self, user):
        """Looks up the user's home location."""

        try:
            return self._geocoder[user.get('home')]
        except (DataError, KeyError) as e:
            raise DataError(e)

    def _observer(self, location):
        """Creates an Astral observer for a geocoded location."""

        return Observer(latitude=location.latitude,
                        longitude=location.longitude,
                        elevation=location.elevation)

    def _sunrise(self, location, time, zone):
        """Calculates sunrise for a geocoded location."""

        return sunrise(self._observer(location),
                       date=time.date(),
                       tzinfo=zone)

    def _sunset(self, location, time, zone):
        """Calculates sunset for a geocoded location."""

        return sunset(self._observer(location),
                      date=time.date(),
                      tzinfo=zone)

    def rewrite_cron(self, cron, after, user):
        """Replaces references to sunrise and sunset in a cron expression."""

        # Skip if there is nothing to rewrite.
        if 'sunrise' not in cron and 'sunset' not in cron:
            return cron

        # Determine the first two days of the cron expression after the
        # reference, which covers all candidate sunrises and sunsets.
        yesterday = after - timedelta(days=1)
        midnight_cron = cron.replace('sunrise', '0 0').replace('sunset', '0 0')
        try:
            first_day = croniter(midnight_cron, yesterday).get_next(datetime)
            second_day = croniter(midnight_cron, first_day).get_next(datetime)
        except ValueError as e:
            raise DataError(e)

        zone = self._local_time.zone(user)
        try:
            home = self._home_location(user)
        except DataError as e:
            raise DataError(e)

        # Calculate the closest future sunrise time and replace the term in the
        # cron expression with minutes and hours.
        if 'sunrise' in cron:
            try:
                sunrises = map(lambda x: self._sunrise(home, x, zone),
                               [first_day, second_day])
                next_sunrise = min(filter(lambda x: x >= after, sunrises))
            except ValueError as e:
                raise DataError(e)
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
            try:
                sunsets = map(lambda x: self._sunset(home, x, zone),
                              [first_day, second_day])
                next_sunset = min(filter(lambda x: x >= after, sunsets))
            except ValueError as e:
                raise DataError(e)
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
        time = self._local_time.now(user)
        zone = self._local_time.zone(user)
        try:
            home = self._home_location(user)
            sunrise_time = self._sunrise(home, time, zone)
            sunset_time = self._sunset(home, time, zone)
        except (DataError, ValueError) as e:
            raise DataError(e)

        is_daylight = time > sunrise_time and time < sunset_time

        info('Daylight: %s (%s)' % (is_daylight,
                                    time.strftime('%A %B %d %Y %H:%M:%S %Z')))

        return is_daylight

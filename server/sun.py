from astral import Astral
from astral import AstralError
from croniter import croniter
from datetime import datetime
from datetime import timedelta
from logging import info

from firestore import DataError
from geocoder import GeocoderWrapper
from local_time import LocalTime


class Sun(object):
    """A wrapper around a calculator for sunrise and sunset times."""

    def __init__(self, geocoder):
        self._astral = Astral(geocoder=GeocoderWrapper, wrapped=geocoder)
        self._local_time = LocalTime(geocoder)

    def rewrite_cron(self, cron, reference, user, forward=True):
        """Replaces references to sunrise and sunset in a cron expression."""

        # Skip if there is nothing to rewrite.
        if 'sunrise' not in cron and 'sunset' not in cron:
            return cron

        # Determine the two days surrounding the cron expression for the
        # reference time, which covers all candidate sunrises and sunsets.
        yesterday = reference - timedelta(days=2)
        midnight_cron = cron.replace('sunrise', '0 0').replace('sunset', '0 0')
        try:
            prev_day = croniter(midnight_cron, yesterday).get_next(datetime)
            current_day = croniter(midnight_cron, prev_day).get_next(datetime)
            next_day = croniter(midnight_cron, current_day).get_next(datetime)

        except ValueError as e:
            raise DataError(e)

        zone = self._local_time.zone(user)
        try:
            home = self._astral[user.get('home')]
        except (AstralError, KeyError) as e:
            raise DataError(e)

        # Set the candidate days and filter based on direction
        candidate_days = []
        direction_filter = None
        sorter = None

        def forward_filter(x):
            return x >= reference

        def backward_filter(x):
            return x <= reference

        if forward:
            candidate_days.extend([current_day, next_day])
            direction_filter = forward_filter
            sorter = min
        else:
            candidate_days.extend([prev_day, current_day])
            direction_filter = backward_filter
            sorter = max

        # Calculate the closest sunrise time and replace the term in the
        # cron expression with minutes and hours.
        if 'sunrise' in cron:
            sunrises = map(
                    lambda x: home.sunrise(x).astimezone(zone),
                    candidate_days)
            next_sunrise = sorter(filter(direction_filter, sunrises))
            sunrise_cron = cron.replace('sunrise', '%d %d' % (
                next_sunrise.minute, next_sunrise.hour))
            info('Rewrote cron: (%s) -> (%s), reference %s' % (
                cron,
                sunrise_cron,
                reference.strftime('%A %B %d %Y %H:%M:%S %Z')))
            return sunrise_cron

        # Calculate the closest future sunset time and replace the term in the
        # cron expression with minutes and hours.
        if 'sunset' in cron:
            sunsets = map(
                    lambda x: home.sunset(x).astimezone(zone),
                    candidate_days)
            next_sunset = sorter(filter(direction_filter, sunsets))
            sunset_cron = cron.replace('sunset', '%d %d' % (next_sunset.minute,
                                                            next_sunset.hour))
            info('Rewrote cron: (%s) -> (%s), reference %s' % (
                cron,
                sunset_cron,
                reference.strftime('%A %B %d %Y %H:%M:%S %Z')))
            return sunset_cron

    def is_daylight(self, user):
        """Calculates whether the sun is currently up."""

        # Find the sunrise and sunset times for today.
        time = self._local_time.now(user)
        zone = self._local_time.zone(user)
        try:
            home = self._astral[user.get('home')]
        except (AstralError, KeyError) as e:
            raise DataError(e)
        sunrise = home.sunrise(time).astimezone(zone)
        sunset = home.sunset(time).astimezone(zone)

        is_daylight = time > sunrise and time < sunset

        info('Daylight: %s (%s)' % (is_daylight,
                                    time.strftime('%A %B %d %Y %H:%M:%S %Z')))

        return is_daylight

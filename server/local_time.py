from datetime import datetime
from logging import error
from pytz import timezone
from pytz import utc


class LocalTime(object):
    """A wrapper around the current time in the user's time zone."""

    def __init__(self, geocoder):
        self.geocoder = geocoder

    def now(self, user):
        """Calculates the current localized date and time."""

        utc_time = utc.localize(datetime.utcnow())
        now = utc_time.astimezone(self.zone(user))

        return now

    def zone(self, user):
        """Returns the time zone at the user's home address."""

        try:
            home = user.get('home')
            location = self.geocoder[home]
            return timezone(location.timezone)
        except KeyError as e:
            error('Failed to get time zone: %s' % e)
            return utc

from astral import AstralError
from datetime import datetime
from pytz import timezone
from pytz import utc

from firestore import DataError


class LocalTime(object):
    """A wrapper around the current time in the user's time zone."""

    def __init__(self, geocoder):
        self._geocoder = geocoder

    def utc_now(self):
        """Calculates the current UTC date and time."""

        return utc.localize(datetime.utcnow())

    def now(self, user):
        """Calculates the current localized date and time."""

        now = self.utc_now().astimezone(self.zone(user))

        return now

    def zone(self, user):
        """Returns the time zone at the user's home address."""

        try:
            home = user.get('home')
            if not home:
                raise DataError('Missing home address')
            location = self._geocoder[home]
            return timezone(location.timezone)
        except (AstralError, KeyError) as e:
            raise DataError(e)

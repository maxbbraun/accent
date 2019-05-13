from astral import AstralError
from datetime import datetime
from pytz import timezone
from pytz import utc

from firestore import DataError


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
            if not home:
                raise DataError('Missing home address')
            location = self.geocoder[home]
            return timezone(location.timezone)
        except (AstralError, KeyError) as e:
            raise DataError(e)

from datetime import datetime
from pytz import timezone
from pytz import utc


class LocalTime(object):
    """A wrapper around the current time in the user's time zone."""

    def now(self, user):
        """Calculates the current localized date and time."""

        utc_time = utc.localize(datetime.utcnow())
        now = utc_time.astimezone(self.zone(user))

        return now

    def zone(self, user):
        """Gives the user's time zone."""

        return timezone(user.get('time_zone'))

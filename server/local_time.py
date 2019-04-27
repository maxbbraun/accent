from datetime import datetime
from pytz import timezone
from pytz import utc


class LocalTime:
    """A wrapper around the current time in the user's time zone."""

    def __init__(self, user):
        self.timezone = timezone(user.get("time_zone"))

    def now(self):
        """Calculates the current localized date and time."""

        utc_time = utc.localize(datetime.utcnow())
        now = utc_time.astimezone(self.timezone)

        return now

    def zone(self):
        """Gives the user's time zone."""

        return self.timezone

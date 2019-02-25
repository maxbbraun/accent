from datetime import datetime
from pytz import timezone
from pytz import utc

# The time zone used for scheduling and requests.
TIMEZONE = timezone("US/Pacific")


def get_now():
    """Calculates the current date and time."""

    utc_now = utc.localize(datetime.utcnow())
    now = utc_now.astimezone(TIMEZONE)

    return now

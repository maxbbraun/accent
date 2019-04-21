from datetime import datetime
from pytz import utc

from user_data import TIMEZONE


def now():
    """Calculates the current localized date and time."""

    utc_time = utc.localize(datetime.utcnow())
    time = utc_time.astimezone(TIMEZONE)

    return time

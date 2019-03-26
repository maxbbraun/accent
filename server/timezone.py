from datetime import datetime
from pytz import utc

from user_data import TIMEZONE


def get_now():
    """Calculates the current localized date and time."""

    utc_now = utc.localize(datetime.utcnow())
    now = utc_now.astimezone(TIMEZONE)

    return now

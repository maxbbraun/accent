from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from datetime import datetime
from pytz import utc

from user_data import TIMEZONE


def now():
    """Calculates the current localized date and time."""

    utc_time = utc.localize(datetime.utcnow())
    time = utc_time.astimezone(TIMEZONE)

    return time

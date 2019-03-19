from datetime import time

from artwork import get_artwork_image
from commute import get_commute_image
from g_calendar import get_calendar_image
from timezone import TIMEZONE

# The schedule determining when to wake and which images to show. Each entry
# defines a name, a cron expression for the start time, and a function to
# generate the image. The end time is the start time of the next entry.
SCHEDULE = [
    {
        "name": "Weekday Morning - Commute",
        "start": "30 6 * * 1-5",
        "image": get_commute_image
    },
    {
        "name": "Weekday Day - Artwork",
        "start": "0 9 * * 1-5",
        "image": get_artwork_image
    },
    {
        "name": "Weekend Morning - Calendar",
        "start": "0 8 * * 6,0",
        "image": get_calendar_image
    },
    {
        "name": "Weekend Day - Artwork",
        "start": "0 12 * * 6,0",
        "image": get_artwork_image
    }
]

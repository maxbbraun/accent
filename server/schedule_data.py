from artwork import get_artwork_image
from commute import get_commute_image
from g_calendar import get_calendar_image

# The schedule determining when to wake and which images to show. Each entry
# defines a name, a cron expression for the start time, and a function to
# generate the image. The end time is the start time of the next entry. The
# cron expressions additionally support the keywords "sunrise" and "sunset"
# instead of hours and minutes.
SCHEDULE = [
    # Weekdays:
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
    # Weekends:
    {
        "name": "Weekend Morning - Calendar",
        "start": "sunrise * * 6,0",
        "image": get_calendar_image
    },
    {
        "name": "Weekend Day - Artwork",
        "start": "0 12 * * 6,0",
        "image": get_artwork_image
    }
]

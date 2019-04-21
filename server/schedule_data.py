from city import city_image
from commute import commute_image
from g_calendar import calendar_image

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
        "image": commute_image
    },
    {
        "name": "Weekday Day - City",
        "start": "0 9 * * 1-5",
        "image": city_image
    },
    {
        "name": "Weekday Night - City",
        "start": "sunset * * 1-5",
        "image": city_image
    },
    # Weekends:
    {
        "name": "Weekend Morning - Calendar",
        "start": "sunrise * * 6,0",
        "image": calendar_image
    },
    {
        "name": "Weekend Day - City",
        "start": "0 12 * * 6,0",
        "image": city_image
    },
    {
        "name": "Weekend Night - City",
        "start": "sunset * * 6,0",
        "image": city_image
    }
]

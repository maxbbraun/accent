from calendar import Calendar
from calendar import monthrange
from calendar import SUNDAY
from collections import Counter
from datetime import datetime
from datetime import timedelta
from dateutil.parser import parse
from googleapiclient import discovery
from googleapiclient.http import build_http
from logging import error
from logging import warning
from oauth2client.file import Storage
from PIL import Image
from PIL.ImageDraw import Draw

from graphics import draw_text
from graphics import SUBVARIO_CONDENSED_MEDIUM
from timezone import get_now

# The file containing Google Calendar API authentication secrets.
CLIENT_SECRETS_FILE = "g_calendar_secrets.json"

# The file containing Google Calendar API authentication credentials.
CREDENTIALS_STORAGE_FILE = "g_calendar_credentials.json"

# The error shown for missing authentication credentials.
CREDENTIALS_ERROR = (
    "Update g_calendar_secrets.json and g_calendar_credentials.json by followi"
    "ng these instructions: https://colab.research.google.com/drive/1mcgu_8cxx"
    "b-MMDKICr8oy9kFPSFPYlZ7#sandboxMode=true&scrollTo=ThqaE4cyA4R1")

# The name of the Google Calendar API.
API_NAME = "calendar"

# The Google Calendar API version.
API_VERSION = "v3"

# The ID of the calendar to show.
CALENDAR_ID = "primary"

# The number of days in a week.
DAYS_IN_WEEK = 7

# The maximum numer of (partial) weeks in a month.
WEEKS_IN_MONTH = 6

# The color of the image background.
BACKGROUND_COLOR = (255, 255, 255)

# The color used for days.
NUMBER_COLOR = (0, 0, 0)

# The color used for the current day and events.
TODAY_COLOR = (255, 255, 255)

# The squircle image file.
SQUIRCLE_FILE = "assets/squircle.gif"

# The dot image file.
DOT_FILE = "assets/dot.gif"

# The offset used to vertically center the numbers in the squircle.
NUMBER_Y_OFFSET = 1

# The horizontal margin between dots.
DOT_MARGIN = 4

# The vertical offset between dots and numbers.
DOT_OFFSET = 16

# The color used to highlight the current day and events.
HIGHLIGHT_COLOR = (255, 0, 0)

# The maximum number of events to show.
MAX_EVENTS = 3


def _get_days_range(start, end):
    """Returns a list of days of the month between two datetimes."""

    # Exclude the exact end time to avoid counting the last day if
    # the end falls exactly on midnight.
    end -= timedelta(microseconds=1)

    return range(start.day, end.day + 1)


def _get_event_counts(now):
    """Retrieves a daily count of events using the Google Calendar API."""

    event_counts = Counter()

    # Read the credentials from file or use the auth flow to create it.
    storage = Storage(CREDENTIALS_STORAGE_FILE)
    credentials = storage.get()
    if not credentials or credentials.invalid:
        error(CREDENTIALS_ERROR)
        return event_counts

    # Create an authorized connection to the API.
    http = build_http()
    if credentials.access_token_expired:
        try:
            credentials.refresh(http)
            storage.put(credentials)
        except IOError as e:
            warning("Failed to save credentials: %s", e)
    authed_http = credentials.authorize(http=http)
    service = discovery.build(API_NAME, API_VERSION, http=authed_http)

    # Process calendar events for each day of the current month.
    first_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    _, last_day = monthrange(now.year, now.month)
    last_date = first_date.replace(day=last_day)
    page_token = None
    while True:
        # Request this month's events.
        request = service.events().list(calendarId=CALENDAR_ID,
                                        timeMin=first_date.isoformat(),
                                        timeMax=last_date.isoformat(),
                                        singleEvents=True,
                                        pageToken=page_token)
        response = request.execute()

        # Iterate over the events from the current page.
        for event in response["items"]:
            try:
                # Count regular events.
                start = parse(event["start"]["dateTime"])
                end = parse(event["end"]["dateTime"])
                for day in _get_days_range(start, end):
                    event_counts[day] += 1
            except KeyError:
                pass

            try:
                # Count all-day events.
                start = datetime.strptime(event["start"]["date"], "%Y-%m-%d")
                end = datetime.strptime(event["end"]["date"], "%Y-%m-%d")
                for day in _get_days_range(start, end):
                    event_counts[day] += 1
            except KeyError:
                pass

        # Move to the next page or stop.
        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return event_counts


def get_calendar_image(width, height):
    """Generates an image with a calendar view."""

    # Show a calendar relative to the current date.
    now = get_now()

    # Get the number of events per day from the API.
    event_counts = _get_event_counts(now)

    # Create a blank image.
    image = Image.new(mode="RGB", size=(width, height), color=BACKGROUND_COLOR)
    draw = Draw(image)

    # Determine the spacing of the days in the image.
    x_stride = width // (DAYS_IN_WEEK + 1)
    y_stride = height // (WEEKS_IN_MONTH + 1)

    # Get this month's calendar.
    calendar = Calendar(firstweekday=SUNDAY)
    weeks = calendar.monthdayscalendar(now.year, now.month)

    # Draw each week in a row.
    for week_index in range(len(weeks)):
        week = weeks[week_index]

        # Draw each day in a column.
        for day_index in range(len(week)):
            day = week[day_index]

            # Ignore days from other months.
            if day == 0:
                continue

            # Determine the position of this day in the image.
            x = (day_index + 1) * x_stride
            y = (week_index + 1) * y_stride

            # Mark the current day with a squircle.
            if day == now.day:
                squircle = Image.open(SQUIRCLE_FILE).convert(mode="RGBA")
                squircle_xy = (x - squircle.size[0] // 2,
                               y - squircle.size[1] // 2)
                draw.bitmap(squircle_xy, squircle, HIGHLIGHT_COLOR)
                number_color = TODAY_COLOR
                event_color = TODAY_COLOR
            else:
                number_color = NUMBER_COLOR
                event_color = HIGHLIGHT_COLOR

            # Draw the day of the month number.
            number = str(day)
            draw_text(number, SUBVARIO_CONDENSED_MEDIUM, number_color,
                      xy=(x, y - NUMBER_Y_OFFSET), image=image)

            # Draw a dot for each event.
            num_events = min(MAX_EVENTS, event_counts[day])
            dot = Image.open(DOT_FILE).convert(mode="RGBA")
            if num_events > 0:
                events_width = (num_events * dot.size[0] +
                                (num_events - 1) * DOT_MARGIN)
                for event_index in range(num_events):
                    event_offset = (event_index * (dot.size[0] +
                                    DOT_MARGIN) - events_width // 2)
                    dot_xy = [x + event_offset,
                              y + DOT_OFFSET - dot.size[0] // 2]
                    draw.bitmap(dot_xy, dot, event_color)

    return image

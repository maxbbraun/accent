from calendar import day_abbr
from croniter import croniter
from datetime import datetime
from datetime import timedelta
from logging import error
from logging import info
from PIL import Image
from PIL.ImageDraw import Draw

from artwork import Artwork
from google_calendar import GoogleCalendar
from graphics import draw_text
from graphics import SCREENSTAR_SMALL_REGULAR
from city import City
from commute import Commute
from content import ContentError
from content import ImageContent
from everyone import Everyone
from firestore import DataError
from local_time import LocalTime
from sun import Sun

# The client sleep duration may be early by a few minutes, so we add a buffer
# to avoid waking up twice in a row.
DELAY_BUFFER_S = 15 * 60

# The background color of the timeline image.
TIMELINE_BACKGROUND = (255, 255, 255)

# The foreground color of the timeline image.
TIMELINE_FOREGROUND = (0, 0, 0)

# The highlight color of the timeline image.
TIMELINE_HIGHLIGHT = (255, 0, 0)

# The width of the timeline image in pixels.
TIMELINE_WIDTH = 900

# The height of the timeline image in pixels.
TIMELINE_HEIGHT = 50

# The drawable width of the timeline, leaving room at the end.
TIMELINE_DRAW_WIDTH = TIMELINE_WIDTH - 1

# The width of lines drawn in the timeline.
TIMELINE_LINE_WIDTH = 1

# The dash length of lines drawn in the timeline.
TIMELINE_LINE_DASH = 2


class Schedule(ImageContent):
    """A database-backed schedule determining which images to show at request
    time and when to wake up from sleep for the next request.

    The schedule is a list of maps, each containing:
     'name': A human-readable name for this entry.
    'start': A cron expression for the start time of this entry. (The end time
             is the start time of the next closest entry in time.) The cron
             expression syntax additionally supports the keywords 'sunrise' and
             'sunset' instead of hours and minutes, e.g. 'sunrise * * *'.
    'image': The kind of image to show when this entry is active. Valid kinds
             are 'artwork', 'city', 'commute', 'calendar', and 'everyone'.
    """

    def __init__(self, geocoder):
        self._local_time = LocalTime(geocoder)
        self._sun = Sun(geocoder)
        self._artwork = Artwork()
        self._city = City(geocoder)
        self._commute = Commute(geocoder)
        self._calendar = GoogleCalendar(geocoder)
        self._everyone = Everyone(geocoder)

    def _next(self, cron, after, user):
        """Finds the next time matching the cron expression."""

        try:
            cron = self._sun.rewrite_cron(cron, after, user)
        except DataError as e:
            raise ContentError(e)

        try:
            return croniter(cron, after).get_next(datetime)
        except ValueError as e:
            raise ContentError(e)

    def _previous(self, cron, before, user):
        """Finds the previous time matching the cron expression."""

        try:
            cron = self._sun.rewrite_cron(cron, before, user, False)
        except DataError as e:
            raise ContentError(e)

        try:
            return croniter(cron, before).get_prev(datetime)
        except ValueError as e:
            raise ContentError(e)

    def _image(self, kind, user, width, height):
        """Creates an image based on the kind."""

        if kind == 'artwork':
            content = self._artwork
        elif kind == 'city':
            content = self._city
        elif kind == 'commute':
            content = self._commute
        elif kind == 'calendar':
            content = self._calendar
        elif kind == 'everyone':
            content = self._everyone
        else:
            error('Unknown image kind: %s' % kind)
            return None

        return content.image(user, width, height)

    def image(self, user, width, height):
        """Generates the current image based on the schedule."""

        # Find the current schedule entry by parsing the cron expressions.
        try:
            time = self._local_time.now(user)
        except DataError as e:
            raise ContentError(e)

        entries = [(self._previous(entry['start'], time, user), entry)
                   for entry in user.get('schedule')]

        if not entries:
            raise ContentError('Empty schedule')

        # Use the most recent past entry.
        latest_datetime, latest_entry = max(entries, key=lambda x: x[0])

        # Generate the image from the current schedule entry.
        info('Using image from schedule entry: %s (%s, %s)' % (
             latest_entry['name'],
             latest_entry['start'],
             latest_datetime.strftime('%A %B %d %Y %H:%M:%S %Z')))
        image = self._image(latest_entry['image'], user, width, height)

        return image

    def delay(self, user):
        """Calculates the delay in milliseconds to the next schedule entry."""

        # Find the next schedule entry by parsing the cron expressions.
        try:
            time = self._local_time.now(user)
        except DataError as e:
            raise ContentError(e)
        entries = [(self._next(entry['start'], time, user), entry)
                   for entry in user.get('schedule')]
        if not entries:
            raise ContentError('Empty schedule')
        next_datetime, next_entry = min(entries, key=lambda x: x[0])

        # Calculate the delay in milliseconds.
        seconds = (next_datetime - time).total_seconds()
        seconds += DELAY_BUFFER_S
        milliseconds = int(seconds * 1000)
        info('Using time from schedule entry: %s (%s, %s, in %d ms)' % (
             next_entry['name'],
             next_entry['start'],
             next_datetime.strftime('%A %B %d %Y %H:%M:%S %Z'),
             milliseconds))

        return milliseconds

    def empty_timeline(self):
        """Generates an empty timeline image."""

        image = Image.new(mode='RGB', size=(TIMELINE_WIDTH, TIMELINE_HEIGHT),
                          color=TIMELINE_BACKGROUND)
        draw = Draw(image)

        # Draw each day of the week.
        num_days = len(day_abbr)
        for day_index in range(num_days):
            x = TIMELINE_DRAW_WIDTH * day_index / num_days

            # Draw a dashed vertical line.
            for y in range(0, TIMELINE_HEIGHT, 2 * TIMELINE_LINE_DASH):
                draw.line([(x, y), (x, y + TIMELINE_LINE_DASH - 1)],
                          fill=TIMELINE_FOREGROUND, width=TIMELINE_LINE_WIDTH)

            # Draw the abbreviated day name.
            name = day_abbr[day_index]
            day_x = x + TIMELINE_DRAW_WIDTH / num_days / 2
            day_y = TIMELINE_HEIGHT - SCREENSTAR_SMALL_REGULAR['height']
            draw_text(name, SCREENSTAR_SMALL_REGULAR, TIMELINE_FOREGROUND,
                      xy=(day_x, day_y), anchor=None, box_color=None,
                      box_padding=0, border_color=None, border_width=0,
                      image=image, draw=draw)

        # Draw another dashed line at the end.
        for y in range(0, TIMELINE_HEIGHT, 2 * TIMELINE_LINE_DASH):
            draw.line([(TIMELINE_DRAW_WIDTH, y),
                       (TIMELINE_DRAW_WIDTH, y + TIMELINE_LINE_DASH - 1)],
                      fill=TIMELINE_FOREGROUND, width=TIMELINE_LINE_WIDTH)

        return image

    def timeline(self, user):
        """Generates a timeline image of the schedule for settings."""

        image = self.empty_timeline()
        draw = Draw(image)

        # Find the user or return the empty timeline.
        try:
            now = self._local_time.now(user)
        except DataError as e:
            return image

        # Start the timeline with the most recent beginning of the week.
        start = now.replace(hour=0, minute=0, second=0)
        start -= timedelta(days=start.weekday())
        stop = start + timedelta(weeks=1)
        start_timestamp = datetime.timestamp(start)
        stop_timestamp = datetime.timestamp(stop)
        timestamp_span = stop_timestamp - start_timestamp

        # Draw a dashed line in highlight color at the current time.
        now_timestamp = datetime.timestamp(now)
        now_x = TIMELINE_DRAW_WIDTH * (
            now_timestamp - start_timestamp) / timestamp_span
        for y in range(0, TIMELINE_HEIGHT, 2 * TIMELINE_LINE_DASH):
            draw.line([(now_x, y), (now_x, y + TIMELINE_LINE_DASH - 1)],
                      fill=TIMELINE_HIGHLIGHT, width=TIMELINE_LINE_WIDTH)

        # Generate the schedule throughout the week.
        entries = user.get('schedule')
        if not entries:
            # Empty timeline.
            return image
        for i in range(len(entries)):
            entries[i]['index'] = i
        time = start
        while time < stop:
            # Find the next entry.
            next_entries = [(self._next(entry['start'], time, user),
                             entry['index'], entry) for entry in entries]
            next_datetime, next_index, next_entry = min(next_entries,
                                                        key=lambda x: x[0])

            # Draw the entry's index and a vertical line, with a tilde to mark
            # the variable sunrise and sunset times.
            timestamp = datetime.timestamp(next_datetime)
            x = TIMELINE_DRAW_WIDTH * (
                timestamp - start_timestamp) / timestamp_span
            y = TIMELINE_HEIGHT / 2
            text = str(next_index + 1)
            next_entry_start = next_entry['start']
            if 'sunrise' in next_entry_start or 'sunset' in next_entry_start:
                text = '~' + text
            box = draw_text(text, SCREENSTAR_SMALL_REGULAR,
                            TIMELINE_FOREGROUND, xy=(x, y), anchor=None,
                            box_color=None, box_padding=4, border_color=None,
                            border_width=0, image=image, draw=draw)
            draw.line([(x, 0), (x, box[1])], fill=TIMELINE_FOREGROUND, width=1)

            # Jump to the next entry.
            time = next_datetime

        return image

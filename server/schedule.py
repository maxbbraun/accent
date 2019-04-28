from croniter import croniter
from datetime import datetime
from datetime import timedelta
from logging import error
from logging import info

from artwork import Artwork
from google_calendar import GoogleCalendar
from city import City
from commute import Commute
from local_time import LocalTime
from sun import Sun

# The client sleep duration may be early by a few minutes, so we add a buffer
# to avoid waking up twice in a row.
DELAY_BUFFER_S = 15 * 60


class Schedule:
    """A database-backed schedule determining which images to show at request
    time and when to wake up from sleep for the next request.

    The schedule is a list of maps, each containing:
     "name": A human-readable name for this entry.
    "start": A cron expression for the start time of this entry. (The end time
             is the start time of the next closest entry in time.) The cron
             expression syntax additionally supports the keywords "sunrise" and
             "sunset" instead of hours and minutes, e.g. "sunrise * * *".
    "image": The kind of image to show when this entry is active. Valid kinds
             are "artwork", "city", "commute", and "calendar".
    """

    def __init__(self, key, user):
        self.local_time = LocalTime(user)
        self.sun = Sun(user)
        self.schedule = user.get("schedule")
        self.artwork = Artwork(user)
        self.city = City(user)
        self.commute = Commute(user)
        self.calendar = GoogleCalendar(key, user)

    def _next(self, cron, after):
        """Finds the next time matching the cron expression."""

        cron = self.sun.rewrite_cron(cron, after)
        return croniter(cron, after).get_next(datetime)

    def _image(self, kind):
        """Creates an image based on the kind."""

        if kind == "artwork":
            return self.artwork.image()

        if kind == "city":
            return self.city.image()

        if kind == "commute":
            return self.commute.image()

        if kind == "calendar":
            return self.calendar.image()

        error("Unknown image kind: %s" % kind)
        return None

    def image(self):
        """Generates the current image based on the schedule."""

        # Find the current schedule entry by parsing the cron expressions.
        time = self.local_time.now()
        today = time.replace(hour=0, minute=0, second=0, microsecond=0)
        while True:
            entries = [(self._next(entry["start"], today), entry)
                       for entry in self.schedule]
            past_entries = list(filter(lambda x: x[0] <= time, entries))

            # Use the most recent past entry.
            if past_entries:
                latest_datetime, latest_entry = max(past_entries,
                                                    key=lambda x: x[0])
                break

            # If there were no past entries, try the previous day.
            today -= timedelta(days=1)

        # Generate the image from the current schedule entry.
        info("Using image from schedule entry: %s (%s, %s)" % (
             latest_entry["name"],
             latest_entry["start"],
             latest_datetime.strftime("%A %B %d %Y %H:%M:%S %Z")))
        image = self._image(latest_entry["image"])

        return image

    def delay(self):
        """Calculates the delay in milliseconds to the next schedule entry."""

        # Find the next schedule entry by parsing the cron expressions.
        time = self.local_time.now()
        entries = [(self._next(entry["start"], time), entry)
                   for entry in self.schedule]
        next_datetime, next_entry = min(entries, key=lambda x: x[0])

        # Calculate the delay in milliseconds.
        seconds = (next_datetime - time).total_seconds()
        seconds += DELAY_BUFFER_S
        milliseconds = int(seconds * 1000)
        info("Using time from schedule entry: %s (%s, %s, in %d ms)" % (
             next_entry["name"],
             next_entry["start"],
             next_datetime.strftime("%A %B %d %Y %H:%M:%S %Z"),
             milliseconds))

        return milliseconds

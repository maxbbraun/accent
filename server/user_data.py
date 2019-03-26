from pytz import timezone

# The key for the Google Directions and Static Map APIs.
# https://cloud.google.com/maps-platform/#get-started
MAPS_API_KEY = "MAPS_API_KEY"

# The home address for the commute.
HOME_ADDRESS = "HOME_ADDRESS"

# The work address for the commute.
WORK_ADDRESS = "WORK_ADDRESS"

# The travel mode for the commute.
# https://developers.google.com/maps/documentation/directions/intro#TravelModes
TRAVEL_MODE = "TRAVEL_MODE"

# The time zone used for the current time.
TIMEZONE = timezone("US/Pacific")

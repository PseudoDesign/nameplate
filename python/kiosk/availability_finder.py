from datetime import timedelta, datetime
import kiosk.outlook_service


def get_quarter_hour_floor(time):
    """
    Rounds down time to the nearest hour
    :param time: a datetime object
    :return: a datetime object
    """
    return time - timedelta(minutes=time.minute % 15, seconds=time.second, microseconds=time.microsecond)


def get_availability(auth_token, email, start_time):
    """
    Determine if a room if available for various durations.  Note that all time offsets are relative
    to the quarter hour floor.
    :param auth_token:
    :param email:
    :param start_time:
    :return: A dictionary showing the availability for 15, 30, and 60 minutes from 'start_time'.  example:
    {
        15: True,
        30: False,
        60: False
    }
    """
    availability = {
        15: None,
        30: None,
        45: None,
        60: None
    }
    start_floor = get_quarter_hour_floor(start_time)
    for duration in availability:
        r = kiosk.outlook_service.find_meeting_times(auth_token, email, start_floor, duration)
        if r is None:
            return None
        # If a meeting time suggestion was returned, the user is available.
        availability[duration] = len(r['meetingTimeSuggestions']) > 0
    availability['start_time'] = start_floor
    return availability

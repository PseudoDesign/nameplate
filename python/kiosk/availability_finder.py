from datetime import timedelta, datetime
import kiosk.outlook_service


def get_half_hour_floor(time):
    """
    Rounds down time to the nearest hour
    :param time: a datetime object
    :return: a datetime object
    """
    return time - timedelta(minutes=time.minute % 30, seconds=time.second, microseconds=time.microsecond)


def get_availability(auth_token, email, start_time):
    """
    Determine if a room if available for various durations.  Note that all time offsets are relative
    to the half hour floor.
    :param auth_token:
    :param email:
    :param start_time:
    :return: A dictionary showing the availability for 30, 60, and 90 minutes from 'start_time's half hour floor.
    example:
    {
        'start_time': datetime(2018, 1, 15, 6, 30)
        30: True,
        60: False,
        90: False
    }
    """
    availability = {
        30: None,
        60: None,
        90: None
    }
    start_floor = get_half_hour_floor(start_time)
    for duration in availability:
        r = kiosk.outlook_service.find_meeting_times(auth_token, email, start_floor, duration)
        if r is None:
            return None
        # If a meeting time suggestion was returned, the user is available.
        availability[duration] = len(r['meetingTimeSuggestions']) > 0
    availability['start_time'] = start_floor
    return availability

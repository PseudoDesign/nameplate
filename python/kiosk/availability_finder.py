from datetime import timedelta, datetime
import kiosk.outlook_service


def get_half_hour_floor(time):
    """
    Rounds down time to the nearest hour
    :param time: a datetime object
    :return: a datetime object
    """
    return time - timedelta(minutes=time.minute % 30, seconds=time.second, microseconds=time.microsecond)


def get_upcoming_availability(auth_token, email, start_time):
    """
    Determine if a room if available at the following half-hour blocks.  Note that all time offsets are relative
    to the half hour floor.
    :param auth_token:
    :param email:
    :param start_time:
    :return: A dictionary showing the availability for 30, 60, and 90 minutes from 'start_time's half hour floor.
    example:
    {
        'start_time': datetime(2018, 1, 15, 6, 30)
        0: False,
        30: True,
        60: False,
        90: False
    }
    """
    availability = {
        0: False,
        30: False,
        60: False,
        90: False
    }
    duration = timedelta(hours=2)
    start_floor = get_half_hour_floor(start_time)
    r = kiosk.outlook_service.find_meeting_times(
        auth_token,
        email,
        start_floor,
        start_floor + duration + timedelta(seconds=2),
        30
    )
    if r is None:
        return None
    # If a meeting time suggestion was returned, the user is available.
    for time in r.get('meetingTimeSuggestions'):
        start = time.get('meetingTimeSlot').get('start').get('dateTime')
        if start:
            start = kiosk.outlook_service.string_to_datetime(start)
            offset = (start - start_floor).total_seconds() / 60
            availability[offset] = True
    availability['start_time'] = start_floor
    availability['current_time'] = start_time - timedelta(microseconds=start_time.microsecond)
    return availability

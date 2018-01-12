import requests
import uuid
import json
from datetime import datetime, timedelta

graph_endpoint = 'https://graph.microsoft.com/beta{0}'


# Generic API Sending
def make_api_call(method, url, token, user_email, payload = None, parameters = None):
    # Send these headers with all API calls
    headers = { 'User-Agent' : 'python_tutorial/1.0',
                'Authorization' : 'Bearer {0}'.format(token),
                'Accept' : 'application/json',
                'X-AnchorMailbox' : user_email }

    # Use these headers to instrument calls. Makes it easier
    # to correlate requests and responses in case of problems
    # and is a recommended best practice.
    request_id = str(uuid.uuid4())
    instrumentation = { 'client-request-id' : request_id,
                        'return-client-request-id' : 'true' }

    headers.update(instrumentation)

    response = None

    if method.upper() == 'GET':
        response = requests.get(url, headers = headers, params = parameters)
    elif method.upper() == 'DELETE':
        response = requests.delete(url, headers = headers, params = parameters)
    elif method.upper() == 'PATCH':
        headers.update({ 'Content-Type' : 'application/json' })
        response = requests.patch(url, headers = headers, data = json.dumps(payload), params = parameters)
    elif method.upper() == 'POST':
        headers.update({ 'Content-Type' : 'application/json' })
        response = requests.post(url, headers = headers, data = json.dumps(payload), params = parameters)

    return response


def get_rooms(access_token):
    get_rooms_url = graph_endpoint.format("/me/findRooms")

    r = make_api_call('GET', get_rooms_url, access_token, "")

    if r.status_code == requests.codes.ok:
        return r.json()['value']
    else:
        return "{0}: {1}".format(r.status_code, r.text)


def set_room(access_token, room_email):
    pass


def get_url(access_token, url):
    get_user_url = graph_endpoint.format(url)

    r = make_api_call('GET', get_user_url, access_token, "")

    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        return None


def get_user(access_token, room_email):
    return get_url(access_token, "/users/{0}".format(room_email))


def post_request_url(access_token, url, data):
    r = make_api_call('POST', graph_endpoint.format(url), access_token, "", payload=data)

    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        return None



def datetime_to_string(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S")

def find_meeting_times(access_token, user_email, start_time, duration_minutes):
    url = "/me/findMeetingTimes"
    end_time = start_time + timedelta(minutes=duration_minutes, seconds=1)
    data = {
        "attendees": [
            {
                "type": "required",
                "emailAddress": {
                    "address": user_email
                }
            }
        ],
        "timeConstraint": {
            "activityDomain": "unrestricted",
            "timeslots": [
                {
                    "start": {
                        "dateTime": datetime_to_string(start_time),
                        "timeZone": "Mountain Standard Time"
                    },
                    "end": {
                        "dateTime": datetime_to_string(end_time),
                        "timeZone": "Mountain Standard Time"
                    }
                }
            ]
        },
        "meetingDuration": "PT{0}M".format(duration_minutes),
        "minimumAttendeePercentage": "100"
    }
    response = post_request_url(access_token, url, data)
    return response


def get_room_info(access_token, room_email):
    room_user = get_user(access_token, room_email)
    return find_meeting_times(access_token, room_email, datetime.now(), 15)
    if room_user:
        return {
            'name': room_user['displayName'],
            'email': room_email,

        }
    return None


def get_me(access_token):
    get_me_url = graph_endpoint.format('/me')

    # Use OData query parameters to control the results
    #  - Only return the displayName and mail fields
    query_parameters = {'$select': 'displayName,mail'}

    r = make_api_call('GET', get_me_url, access_token, "", parameters = query_parameters)

    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        return "{0}: {1}".format(r.status_code, r.text)
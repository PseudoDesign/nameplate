from urllib.parse import urlencode
from .outlook_service import get_me
import requests
import time
from docker import secrets

# Client ID and secret
client_id = secrets.get("nameplate_api_id")
client_secret = secrets.get("nameplate_api_passkey")

# Constant strings for OAuth2 flow
# The OAuth authority
authority = 'https://login.microsoftonline.com'

# The authorize URL that initiates the OAuth2 client credential flow for admin consent
authorize_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/authorize?{0}')

# The token issuing endpoint
token_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/token')

# The scopes required by the app
scopes = [ 'openid',
           'User.Read.All',
           'offline_access',
           "Calendars.Read",
           "Calendars.ReadWrite",
           "Calendars.Read.Shared",
           "Calendars.ReadWrite.Shared"
           ]


def get_signin_url(redirect_uri):
    # Build the query parameters for the signin url
    params = { 'client_id': client_id,
               'redirect_uri': redirect_uri,
               'response_type': 'code',
               'scope': ' '.join(str(i) for i in scopes)
               }

    signin_url = authorize_url.format(urlencode(params))

    return signin_url


def get_token_from_code(auth_code, redirect_uri):
    # Build the post form for the token request
    post_data = { 'grant_type': 'authorization_code',
                  'code': auth_code,
                  'redirect_uri': redirect_uri,
                  'scope': ' '.join(str(i) for i in scopes),
                  'client_id': client_id,
                  'client_secret': client_secret
                  }

    r = requests.post(token_url, data = post_data)

    try:
        return r.json()
    except:
        return 'Error retrieving token: {0} - {1}'.format(r.status_code, r.text)


def get_token_from_refresh_token(refresh_token, redirect_uri):
    # Build the post form for the token request
    post_data = { 'grant_type': 'refresh_token',
                  'refresh_token': refresh_token,
                  'redirect_uri': redirect_uri,
                  'scope': ' '.join(str(i) for i in scopes),
                  'client_id': client_id,
                  'client_secret': client_secret
                  }

    r = requests.post(token_url, data = post_data)

    try:
        return r.json()
    except:
        return 'Error retrieving token: {0} - {1}'.format(r.status_code, r.text)


def process_auth_code(request, auth_code, redirect_uri):
    token = get_token_from_code(auth_code, redirect_uri)
    access_token = token.get('access_token')

    if access_token is None:
        return False

    user = get_me(access_token)
    refresh_token = token['refresh_token']
    expires_in = token['expires_in']

    # expires_in is in seconds
    # Get current timestamp (seconds since Unix Epoch) and
    # add expires_in to get expiration time
    # Subtract 5 minutes to allow for clock differences
    expiration = int(time.time()) + expires_in - 300

    # Save the token in the session
    request.session['access_token'] = access_token
    request.session['refresh_token'] = refresh_token
    request.session['token_expires'] = expiration
    request.session['user_email'] = user['mail']
    return True


def get_access_token(request, redirect_uri):
    current_token = request.session.get('access_token')
    expiration = request.session.get('token_expires')
    now = int(time.time())
    if not current_token:
        return None
    if now < expiration:
        # Token still valid
        return current_token
    else:
        # Token expired
        refresh_token = request.session.get('refresh_token')
        new_tokens = get_token_from_refresh_token(refresh_token, redirect_uri)

        # Update session
        # expires_in is in seconds
        # Get current timestamp (seconds since Unix Epoch) and
        # add expires_in to get expiration time
        # Subtract 5 minutes to allow for clock differences
        expiration = int(time.time()) + new_tokens['expires_in'] - 300

        # Save the token in the session
        request.session['access_token'] = new_tokens['access_token']
        request.session['refresh_token'] = new_tokens['refresh_token']
        request.session['token_expires'] = expiration

        return new_tokens['access_token']
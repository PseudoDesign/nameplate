from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from .auth_helper import get_signin_url, get_token_from_code, get_access_token
from .outlook_service import get_me
import time


def require_login(view):
    def function_wrapper(request):
        token = get_access_token(request, request.build_absolute_uri(reverse('get_token')))
        if token:
            return view(request, token)
        else:
            return HttpResponseRedirect(reverse('outlook_login'))
    return function_wrapper

@require_login
def home(request, token):
    return render(request, "kiosk/welcome.html")

def outlook_logout(request):
    return render(request, "kiosk/welcome.html")

def outlook_login(request):
    redirect_uri = request.build_absolute_uri(reverse('get_token'))
    signin_url = get_signin_url(redirect_uri)
    context = {
        'signin_url': signin_url,
    }
    return render(request, "kiosk/outlook_login.html", context)

def get_token(request):
    auth_code = request.GET['code']
    redirect_uri = request.build_absolute_uri(reverse('get_token'))
    token = get_token_from_code(auth_code, redirect_uri)
    access_token = token['access_token']
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
    return HttpResponseRedirect(request.build_absolute_uri(reverse('home')))
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import kiosk.auth_helper
import kiosk.outlook_service
import time


def require_login(view):
    def function_wrapper(request):
        token = kiosk.auth_helper.get_access_token(request, request.build_absolute_uri(reverse('get_token')))
        if token:
            return view(request, token)
        else:
            return HttpResponseRedirect(reverse('outlook_login'))
    return function_wrapper

@require_login
def home(request, access_token):
    return render(request, "kiosk/welcome.html")

def outlook_logout(request):
    request.session.clear()
    return HttpResponseRedirect(reverse('outlook_login'))

def outlook_login(request):
    redirect_uri = request.build_absolute_uri(reverse('get_token'))
    signin_url = kiosk.auth_helper.get_signin_url(redirect_uri)
    context = {'signin_url': signin_url}

    token = kiosk.auth_helper.get_access_token(request, request.build_absolute_uri(reverse('get_token')))
    if token:
        context['logged_in'] = True
        context['user_email'] = kiosk.outlook_service.get_me(token)['mail']
        context['logout_link'] = reverse("outlook_logout")
    else:
        context['logged_in'] = False
    return render(request, "kiosk/outlook_login.html", context)

def get_token(request):
    auth_code = request.GET.get('code')

    if kiosk.auth_helper.process_auth_code(request, auth_code, request.build_absolute_uri(reverse('get_token'))):
        return HttpResponseRedirect(reverse('home'))
    else:
        return HttpResponseBadRequest("Code did not generate a valid access token.")
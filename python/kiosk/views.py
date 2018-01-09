from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse
from .authhelper import get_signin_url

# Create your views here.
def welcome(request):
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
    return HttpResponse('Authorization code: {0}'.format(auth_code))
from django.shortcuts import render

# Create your views here.
def welcome(request):
    return render(request, "kiosk/welcome.html")

def outlook_login(request):
    signin_url = "#"
    context = {
        'signin_url': signin_url,
    }
    return render(request, "kiosk/outlook_login.html", context)
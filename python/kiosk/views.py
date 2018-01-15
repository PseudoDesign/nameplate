from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotFound, JsonResponse
import kiosk.auth_helper
import kiosk.outlook_service
import kiosk.availability_finder
from datetime import datetime
from kiosk.forms import SetRoomForm, ScheduleRoomForm


def require_login(view):
    def function_wrapper(request):
        token = kiosk.auth_helper.get_access_token(request, request.build_absolute_uri(reverse('get_token')))
        if token:
            return view(request, token)
        else:
            return HttpResponseRedirect(reverse('outlook_login'))
    return function_wrapper


@require_login
def room_info(request, access_token):
    room_email = request.GET.get('room_email')
    if room_email is None:
        return HttpResponseBadRequest("room_email is required.")
    availability = kiosk.availability_finder.get_upcoming_availability(access_token, room_email, datetime.now())
    user = kiosk.outlook_service.get_user(access_token, room_email)
    if availability is not None and user is not None:
        return JsonResponse({
            "name": user['displayName'],
            "availability": availability
        })
    else:
        return HttpResponseBadRequest("Invalid room_email")


@csrf_protect
@require_login
def set_room(request, access_token):
    if request.method == "POST":
        room = SetRoomForm(request.POST)
        if not room.is_valid():
            return HttpResponseBadRequest("room_email is required.")
        if kiosk.outlook_service.set_room(request.session, access_token, room.cleaned_data['room_email']):
            return HttpResponseRedirect(reverse("home"))
        else:
            return HttpResponseBadRequest("Invalid room_email")
    return HttpResponseRedirect(reverse("home"))


@require_login
def home(request, access_token):
    room_email = request.session.get('room_email')
    user = None
    if room_email:
        user = kiosk.outlook_service.get_user(access_token, room_email)
        display_name = user.get('displayName')
    if not user or not display_name:
        return HttpResponseRedirect(reverse("select_room"))
    context = {
        'display_name': display_name,
        'room_email': room_email,
        'schedule_room_form': ScheduleRoomForm()
    }
    return render(request, "kiosk/welcome.html", context)


@require_login
def select_room(request, access_token):
    rooms = kiosk.outlook_service.get_rooms(access_token)
    if rooms is None:
        return HttpResponseNotFound("Could not get the list of rooms.")
    context = {'rooms': []}
    for room in rooms:
        context['rooms'] += [{
            'form': SetRoomForm(data={'room_email': room['address']}),
            'name': room['name']
        }]
    return render(request, "kiosk/select_room.html", context)


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
    request.session.clear()
    if kiosk.auth_helper.process_auth_code(request, auth_code, request.build_absolute_uri(reverse('get_token'))):
        return HttpResponseRedirect(reverse('home'))
    else:
        return HttpResponseBadRequest("Code did not generate a valid access token.")
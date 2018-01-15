from django import forms
from kiosk.outlook_service import datetime_format


class SetRoomForm(forms.Form):
    room_email = forms.CharField(widget = forms.HiddenInput())


class ScheduleRoomForm(forms.Form):
    start_time = forms.DateTimeField(widget = forms.HiddenInput(), input_formats=[datetime_format])
    duration_minutes = forms.IntegerField(widget = forms.HiddenInput())
    room_email = forms.CharField(widget = forms.HiddenInput())
from django import forms


class SetRoomForm(forms.Form):
    room_email = forms.CharField(widget = forms.HiddenInput())

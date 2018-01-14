from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from datetime import timedelta, datetime
import json
from kiosk import availability_finder as af
from kiosk.outlook_service import datetime_to_string


class TestAvailabilityFinder(TestCase):
    def test_get_half_hour_floor(self):
        test_cases = [
            {
                'input': datetime(2018, 1, 11, 5, 33, 21),
                'output': datetime(2018, 1, 11, 5, 30, 00)
            },
            {
                'input': datetime(2013, 1, 11, 15, 15, 00),
                'output': datetime(2013, 1, 11, 15, 00, 00)
            }
        ]
        for c in test_cases:
            self.assertEqual(af.get_half_hour_floor(c['input']), c['output'])

    @patch("kiosk.outlook_service.find_meeting_times")
    def test_full_availability(self, find_meeting_times):
        now = datetime.now()
        now_floor = af.get_half_hour_floor(now)
        expected_response = {
            'start_time': now_floor,
            0: True,
            30: True,
            60: True,
            90: True
        }
        find_meeting_times.return_value = {'meetingTimeSuggestions': [
            {'meetingTimeSlot': {'start': {'dateTime': datetime_to_string(now_floor + timedelta(minutes=0))}}},
            {'meetingTimeSlot': {'start': {'dateTime': datetime_to_string(now_floor + timedelta(minutes=30)) + ".00"}}},
            {'meetingTimeSlot': {'start': {'dateTime': datetime_to_string(now_floor + timedelta(minutes=60))}}},
            {'meetingTimeSlot': {'start': {'dateTime': datetime_to_string(now_floor + timedelta(minutes=90))}}},
        ]}
        availability = af.get_upcoming_availability("12345", "1@2.com", now)
        self.assertEqual(expected_response, availability)

    @patch("kiosk.outlook_service.find_meeting_times")
    def test_no_availability(self, find_meeting_times):
        now = datetime.now()
        expected_response = {
            'start_time': af.get_half_hour_floor(now),
            0: False,
            30: False,
            60: False,
            90: False
        }
        find_meeting_times.return_value = {'meetingTimeSuggestions': []}
        availability = af.get_upcoming_availability("12345", "1@2.com", now)
        self.assertEqual(expected_response, availability)


class TestGetRoomInfo(TestCase):
    def setUp(self):
        self.client = Client()

    @patch("kiosk.auth_helper.get_access_token")
    def test_no_room_email_returns_400(self, get_access_token):
        get_access_token.return_value = "12345"
        response = self.client.get(reverse("room_info"))
        self.assertEqual(response.status_code, 400)

    @patch("kiosk.auth_helper.get_access_token")
    def test_invalid_room_email_returns_400(self, get_access_token):
        get_access_token.return_value = "12345"
        response = self.client.get(reverse("room_info") + "?room_email=111")
        self.assertEqual(response.status_code, 400)

    @patch("kiosk.outlook_service.get_user")
    @patch("kiosk.availability_finder.get_upcoming_availability")
    @patch("kiosk.auth_helper.get_access_token")
    def test_valid_room_available(self, get_access_token, get_availability, get_user):
        get_user.return_value = {"displayName": "Test Name"}
        get_access_token.return_value = "12345"
        get_availability.return_value = {
            'start_time': af.get_half_hour_floor(datetime.now()),
            0: True,
            30: True,
            60: True,
            90: True
        }
        response = self.client.get(reverse('room_info') + "?room_email=1@2.co")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(get_availability.return_value[30], data['availability']['30'])
        self.assertEqual("Test Name", data['name'])

    @patch("kiosk.outlook_service.get_user")
    @patch("kiosk.availability_finder.get_upcoming_availability")
    @patch("kiosk.auth_helper.get_access_token")
    def test_status_room_occupied(self, get_access_token, get_availability, get_user):
        get_user.return_value = {"displayName": "Test Name"}
        get_access_token.return_value = "12345"
        get_availability.return_value = {
            'start_time': af.get_half_hour_floor(datetime.now()),
            0: False,
            30: True,
            60: True,
            90: True
        }
        response = self.client.get(reverse('room_info') + "?room_email=1@2.co")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(get_availability.return_value[30], data['availability']['30'])
        self.assertEqual("Test Name", data['name'])


class TestSetRoom(TestCase):
    def setUp(self):
        self.client = Client()

    @patch("kiosk.auth_helper.get_access_token")
    def test_no_room_email_returns_400(self, get_access_token):
        get_access_token.return_value = "12345"
        response = self.client.get(reverse("set_room"))
        self.assertEqual(response.status_code, 400)

    @patch("kiosk.outlook_service.set_room")
    @patch("kiosk.auth_helper.get_access_token")
    def test_invalid_room_email_returns_400(self, get_access_token, set_room):
        get_access_token.return_value = "12345"
        set_room.return_value = False
        response = self.client.get(reverse("set_room") + "?room_email=fake")
        self.assertEqual(response.status_code, 400)

    @patch("kiosk.outlook_service.set_room")
    @patch("kiosk.auth_helper.get_access_token")
    def test_valid_room_email_redirects_to_home(self, get_access_token, set_room):
        get_access_token.return_value = "12345"
        set_room.return_value = True
        response = self.client.get(reverse("set_room") + "?room_email=fake@room.me")
        self.assertRedirects(response, reverse('home'), fetch_redirect_response=False)


class TestSelectRoom(TestCase):
    def setUp(self):
        self.client = Client()

    @patch("kiosk.auth_helper.get_access_token")
    @patch("kiosk.outlook_service.get_rooms")
    def test_returns_404_when_rooms_is_none(self, get_rooms, get_access_token):
        get_rooms.return_value = None
        get_access_token.return_value = "12345"
        response = self.client.get(reverse("select_room"))
        self.assertEqual(response.status_code, 404)

    @patch("kiosk.auth_helper.get_access_token")
    @patch("kiosk.outlook_service.get_rooms")
    def test_rooms_passed_to_template(self, get_rooms, get_access_token):
        get_rooms.return_value = [
            {
                "name": "Test Room",
                "email": "test@room.mail"
            }
        ]
        get_access_token.return_value = "12345"
        response = self.client.get(reverse("select_room"))
        self.assertEqual(response.context["rooms"], get_rooms.return_value)


class TestGetToken(TestCase):
    def setUp(self):
        self.client = Client()

    def test_invalid_auth_code_fails_with_400(self):
        response = self.client.get(reverse("get_token") + "?code=fake")
        self.assertEqual(response.status_code, 400)

    def test_no_auth_code_fails_with_400(self):
        response = self.client.get(reverse("get_token"))
        self.assertEqual(response.status_code, 400)

    @patch("kiosk.auth_helper.process_auth_code")
    def test_valid_auth_code_redirects_to_home(self, process_auth_code):
        process_auth_code.return_value = True
        response = self.client.get(reverse("get_token"))
        self.assertRedirects(response, reverse("home"), fetch_redirect_response=False)


class TestHomeView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_redirect_to_login_page_when_no_access_token_is_present(self):
        self.client.session['access_token'] = None
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('outlook_login'))

    @patch("kiosk.auth_helper.get_access_token")
    def test_redirect_to_select_room_when_room_is_not_set(self, get_access_token):
        get_access_token.return_value = "12345"
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('select_room'))

    @patch("kiosk.outlook_service.get_user")
    @patch("kiosk.auth_helper.get_access_token")
    def test_redirect_to_select_room_when_room_is_invalid(self, get_access_token, get_user):
        get_user.return_value = None
        get_access_token.return_value = "12345"
        self.client.session['room_email'] = "1@2.com"
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('select_room'))

    @patch("kiosk.outlook_service.get_user")
    @patch("kiosk.auth_helper.get_access_token")
    def test_provides_room_email_and_display_name_in_context(self, get_access_token, get_user):
        get_user.return_value = {
            "displayName": "Test Room"
        }
        session = self.client.session
        session['room_email'] = "testroom@test.herp"
        session.save()
        get_access_token.return_value = "12345"
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['room_email'], "testroom@test.herp")
        self.assertEqual(response.context['display_name'], "Test Room")


class TestLogoutView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_clears_session_cookies(self):
        self.client.session["test_clear"] = False
        self.client.get(reverse('outlook_logout'))
        self.assertFalse("test_clear" in self.client.session)

    def test_redirects_to_login(self):
        response = self.client.get(reverse('outlook_logout'))
        self.assertRedirects(response, reverse('outlook_login'))

class TestLoginPage(TestCase):
    def setUp(self):
        self.client = Client()

    def test_sign_in_link(self):
        outlook_url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        response = self.client.get(reverse('outlook_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['signin_url'].startswith(outlook_url))

    @patch("kiosk.outlook_service.get_me")
    @patch("kiosk.auth_helper.get_access_token")
    def test_sign_out_link_displays_when_signed_in(self, get_access_token, get_me):
        get_access_token.return_value = "12345"
        get_me.return_value = {'mail': "my@email.com"}
        response = self.client.get(reverse('outlook_login'))
        self.assertEqual(response.context['logout_link'], reverse("outlook_logout"))

    @patch("kiosk.outlook_service.get_me")
    @patch("kiosk.auth_helper.get_access_token")
    def test_logged_in_flag_set_when_logged_in(self, get_access_token, get_me):
        get_access_token.return_value = "12345"
        get_me.return_value = {'mail': "my@email.com"}
        response = self.client.get(reverse('outlook_login'))
        self.assertTrue(response.context['logged_in'])

    def test_logged_in_flag_unset_when_not_logged_in(self):
        response = self.client.get(reverse('outlook_login'))
        self.assertFalse(response.context['logged_in'])

    @patch("kiosk.outlook_service.get_me")
    @patch("kiosk.auth_helper.get_access_token")
    def test_user_email_set_when_logged_in(self, get_access_token, get_me):
        get_access_token.return_value = "12345"
        get_me.return_value = {'mail': "my@email.com"}
        response = self.client.get(reverse('outlook_login'))
        self.assertEqual(response.context['user_email'], "my@email.com")

    def test_user_email_not_set_when_not_logged_in(self):
        response = self.client.get(reverse('outlook_login'))
        self.assertFalse('user_email' in response.context)


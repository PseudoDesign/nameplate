from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from datetime import timedelta, datetime
import json


class TestGetRoomInfo(TestCase):
    def setUp(self):
        self.client = Client()

    @patch("kiosk.auth_helper.get_access_token")
    def test_no_room_email_returns_400(self, get_access_token):
        get_access_token.return_value = "12345"
        response = self.client.get(reverse("room_info"))
        self.assertEqual(response.status_code, 400)

    @patch("kiosk.outlook_service.get_room_info")
    @patch("kiosk.auth_helper.get_access_token")
    def test_invalid_room_email_returns_400(self, get_access_token, get_room_info):
        get_access_token.return_value = "12345"
        get_room_info.return_value = None
        response = self.client.get(reverse("room_info") + "?room_email=111")
        self.assertEqual(response.status_code, 400)

    @patch("kiosk.outlook_service.get_room_info")
    @patch("kiosk.auth_helper.get_access_token")
    def test_valid_room_returns_json_info(self, get_access_token, get_room_info):
        get_access_token.return_value = "12345"
        start_time = datetime.now() - timedelta(minutes=10)
        end_time = datetime.now() + timedelta(minutes=10)
        get_room_info.return_value = {
            'name': "Test Room",
            'email': "test@room.com",
            'current_meeting': {
                'organizer': {
                    'name': "John Doe",
                    'email': "jdoe@test.com"
                },
                'start_time': start_time,
                'end_time': end_time
            },
            'next_meeting': {
                'organizer': {
                    'name': "John Doe",
                    'email': "jdoe@test.com"
                },
                'start_time': start_time + timedelta(days=1),
                'end_time': end_time + timedelta(days=1)
            }
        }
        response = self.client.get(reverse('room_info') + "?room_email=1@2.co")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)['value']
        self.assertEqual(get_room_info.return_value['email'], data['email'])
        self.assertEqual(get_room_info.return_value['name'], data['name'])


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
    def test_valid_room_email_redirects_to_select_room(self, get_access_token, set_room):
        get_access_token.return_value = "12345"
        set_room.return_value = True
        response = self.client.get(reverse("set_room") + "?room_email=fake@room.me")
        self.assertRedirects(response, reverse('select_room'), fetch_redirect_response=False)


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


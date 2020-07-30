from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from userprofile.serializers import ProfileSerializer
from django.contrib.auth.models import User
from userprofile.models import Profile
from .common import test_data
from .common import test_methods
import phonenumbers

TEST_PROFILES = test_data.profiles


class TestAuth(APITestCase):
    def setUp(self):
        for profile in TEST_PROFILES:
            phone_number = phonenumbers.format_number(phonenumbers.parse(
                profile.pop('phone_number'),
                profile.pop('country')), phonenumbers.NumberFormat.E164)

            user1 = User.objects.create_user(
                profile.pop('username'),
                profile.pop('email'),
                profile.pop('password'),
                first_name=profile.pop('first_name', None),
                last_name=profile.pop('last_name', None),
            )
            Profile.object.create(
                user=user1, phone_number=phone_number, **profile)

    def test_login(self):
        TEST_PROFILES = test_data.profiles
        url = reverse('login')
        user_details = {
            'username': TEST_PROFILES[4]['username'],
            'password': TEST_PROFILES[4]['password']
        }
        response = self.client.post(url, user_details, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

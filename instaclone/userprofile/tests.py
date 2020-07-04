# from django.test import TestCase
# from rest_framework.test import APIRequestFactory
from django.contrib.auth.urls import urlpatterns
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from userprofile.models import Profile
import json

profiles = [
    {

        "username": "user1",
        "first_name": "first_name1",
        "email": "email@mail.com",
        "password": "pass1234",
        "bio": "This is my bio",
        "phone_number": {
            "country_code": "27",
            "number": "712414451"
        },
        "is_private": True
    },
    {

        "username": "user2",
        "first_name": "first_name1",
        "email": "email@mail.com",
        "password": "pass1234",
        "bio": "This is my bio",
        "phone_number": {
            "country_code": "27",
            "number": "712414451"
        },
        "is_private": True
    },
    {

        "username": "user3",
        "first_name": "first_name1",
        "email": "email@mail.com",
        "password": "pass1234",
        "bio": "This is my bio",
        "phone_number": {
            "country_code": "27",
            "number": "712414451"
        },
        "is_private": True
    },
    {

        "username": "user7",
        "first_name": "first_name1",
        "email": "email@mail.com",
        "password": "pass1234",
        "bio": "This is my bio",
        "phone_number": {
            "country_code": "27",
            "number": "712414451"
        },
        "is_private": True
    },
    {

        "username": "user6",
        "first_name": "first_name1",
        "email": "email@mail.com",
        "password": "pass1234",
        "bio": "This is my bio",
        "phone_number": {
            "country_code": "27",
            "number": "712414451"
        },
        "is_private": True
    },
    {

        "username": "user4",
        "first_name": "first_name1",
        "email": "email@mail.com",
        "password": "pass1234",
        "bio": "This is my bio",
        "phone_number": {
            "country_code": "27",
            "number": "712414451"
        },
        "is_private": True
    },
    {

        "username": "user5",
        "first_name": "first_name1",
        "email": "email@mail.com",
        "password": "pass1234",
        "bio": "This is my bio",
        "phone_number": {
            "country_code": "27",
            "number": "712414451"
        },
        "is_private": True
    },
]


class ProfileTest(APITestCase):
    def test_create_profile(self):
        """
        Ensure we can create a new profile object.
        """
        url = reverse('profiles-list')
        data = profiles[5]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(
            Profile.objects.get().user.username, data['username'])
        self.assertEqual(
            Profile.objects.get().following.count(), 0)
        self.assertEqual(
            Profile.objects.get().follow_requests_received.count(), 0)

    def test_login(self):
        """
        Ensure profile can login
        """
        # Create profile
        url = reverse('profiles-list')
        data = profiles[5]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(
            Profile.objects.get().user.username, data['username'])

        # Login Attempt
        username = data['username']
        password = data['password']
        data = {'username': username, 'password': password}
        url = reverse('login')
        response = self.client.post(url, data, format='json')
        # Assert Logged in
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check token
        content = json.loads(response.content)
        self.assertEqual(len(content.keys()), 1)
        self.assertEqual(
            list(content)[0].lower(), 'token')

        self.assertEqual(
            content['token'], Profile.objects.get(id=1).user.auth_token.key)

# from django.test import TestCase
# from rest_framework.test import APIRequestFactory
from django.contrib.auth.urls import urlpatterns
from django.db import transaction
from django.db.utils import IntegrityError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core import exceptions
from userprofile.models import Profile
from django.contrib.auth.models import User
from rest_framework import serializers

import json

profiles = [
    {

        "username": "user1",
        "first_name": "first_name1",
        "email": "email1@mail.com",
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
        "first_name": "first_name2",
        "email": "email2@mail.com",
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
        "first_name": "first_name3",
        "email": "email3@mail.com",
        "password": "pass1234",
        "bio": "This is my bio",
        "phone_number": {
            "country_code": "27",
            "number": "712414451"
        },
        "is_private": False
    },
    {

        "username": "user7",
        "first_name": "first_name4",
        "email": "email4@mail.com",
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
        "first_name": "first_name5",
        "email": "email5@mail.com",
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
        "first_name": "first_name6",
        "email": "email6@mail.com",
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
        "first_name": "first_name7",
        "email": "email7@mail.com",
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

    def test_login(self):
        """
        Ensure profile can login
        """
        # Create profiles
        url = reverse('profiles-list')
        for data in profiles:
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Login Attempt
        url = reverse('login')
        for data in profiles:
            data = {
                'username': data['username'],
                'password': data['password'],
            }
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            response_data = json.loads(response.content)
            self.assertTrue(response_data['logged_in'])
            self.assertEqual(
                response_data['token'],
                Profile.objects.get(user__username=data['username'])
                .user.auth_token.key)

    def test_logout(self):
        """
        Ensure profile can logout
        """
        # Create profiles
        url = reverse('profiles-list')
        user_1 = profiles[0]
        user_2 = profiles[1]

        for data in profiles:
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Login Attempt
        url = reverse('login')

        # Login user 1
        data = {
            'username': user_1['username'],
            'password': user_1['password'],
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = json.loads(response.content)
        user_1_token = response_data['token']

        # Login user 2
        data = {
            'username': user_2['username'],
            'password': user_2['password'],
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = json.loads(response.content)
        user_2_token = response_data['token']
        self.assertTrue(response_data['logged_in'])

        self.assertEqual(
            User.objects.filter(auth_token__key=user_1_token).count(), 1)

        self.assertEqual(
            User.objects.filter(auth_token__key=user_2_token).count(), 1)

        # Logout
        url = reverse('logout')
        logged_in_profile = Profile.objects.get(
            user__username=user_1['username'])

        self.client.credentials(
            HTTP_AUTHORIZATION='Token {}'.format(
                logged_in_profile.user.auth_token.key
            ))
        # Logout user 1
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert user 1 logged out

        self.assertEqual(
            User.objects.filter(auth_token__key=user_1_token).count(), 0)

        # Assert user 2 NOT logged out
        self.assertEqual(
            User.objects.filter(auth_token__key=user_2_token).count(), 1)

    def test_create_profile(self):
        """
        Ensure we can create a new profile object.
        """
        url = reverse('profiles-list')
        for profile in profiles:
            response = self.client.post(url, profile, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(
                len(Profile.objects.filter(
                    user__username=profile['username'])), 1)
        self.assertEqual(len(Profile.objects.all()), 7)
        self.assertFalse(Profile.objects.get(
            user__username='user3').is_private)

    def test_read_profile_list(self):
        """
        Ensure we can read a list of profile objects.
        """
        url = reverse('profiles-list')
        for profile in profiles:
            response = self.client.post(url, profile, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            self.assertEqual(
                len(Profile.objects.filter(
                    user__username=profile['username'])), 1)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = json.loads(response.content)
        response_data = sorted(
            response_data, key=lambda profile: profile['username'])
        expected_data = sorted(
            profiles, key=lambda profile: profile['username'])

        self.assertEqual(len(Profile.objects.all()), len(response_data))

        for i in range(len(expected_data)):
            response_profile = response_data[i]
            expected_profile = expected_data[i]
            self.assertEqual(
                response_profile['username'], expected_profile['username'])
            self.assertEqual(
                response_profile['email'], expected_profile['email'])

    def test_read_profile_detail(self):
        """
        Ensure we can read a specific object.
        """
        url = reverse('profiles-list')
        for profile in profiles:
            response = self.client.post(url, profile, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            self.assertEqual(
                len(Profile.objects.filter(
                    user__username=profile['username'])), 1)

        for i in range(len(profiles)):
            url = reverse('profiles-detail', args=[i + 1])
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            response_data = json.loads(response.content)
            self.assertEqual(
                response_data['id'], i + 1)
            self.assertEqual(
                response_data['username'], profiles[i]['username'])
            self.assertEqual(
                response_data['email'], profiles[i]['email'])

    def test_update_profile(self):
        """
        Ensure we can change the data in a profile.
        """
        # Create profiles
        list_url = reverse('profiles-list')
        for data in profiles:
            response = self.client.post(list_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Login
        login_url = reverse('login')
        user = {
            'username': profiles[1]['username'],
            'password': profiles[1]['password'],
        }
        response = self.client.post(login_url, user, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        logged_in_profile = Profile.objects.get(
            user__username=user['username'])

        self.client.credentials(
            HTTP_AUTHORIZATION='Token {}'.format(
                logged_in_profile.user.auth_token.key
            ))

        detail_url = reverse('profiles-detail', args=[logged_in_profile.id])
        updated_user = profiles[1]
        updated_user['bio'] = 'I\'ve been updated'

        # Full update

        response = self.client.put(detail_url, updated_user, format='json')
        response_data = json.loads(response.content)
        logged_in_profile = Profile.objects.get(
            user__username=updated_user['username'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(logged_in_profile.bio, updated_user['bio'])

        # Partial Update
        logged_in_profile = Profile.objects.get(
            user__username=user['username'])

        response = self.client.patch(
            detail_url, {'bio': 'Really'}, format='json')
        logged_in_profile = Profile.objects.get(
            user__username=user['username'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(logged_in_profile.bio, 'Really')

        try:
            # Using try with transaction.atomic() instead of just with
            # prevents a bug that doesn't roll back non consistant transactions
            # by making those transaction atomic.
            #
            # Duplicates should be prevented.
            with transaction.atomic():
                response = self.client.patch(
                    detail_url, {'bio': 'Really', 'username': 'user1'},
                    format='json')
            self.fail('Duplicate question allowed.')
        except IntegrityError:
            pass

        response = self.client.patch(
            detail_url, {'bio': 'Really', 'first_name': 'user1'},
            format='json')
        logged_in_profile = Profile.objects.get(
            user__username=user['username'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(logged_in_profile.user.first_name, 'user1')

        response = self.client.patch(
            detail_url, {'bio': 'Really', 'username': 'user_name_unique'},
            format='json')
        logged_in_profile = Profile.objects.get(
            user__username='user_name_unique')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(logged_in_profile.user.username, 'user_name_unique')

    def test_delete_profile(self):
        """
        Ensure we can destroy a profile object.
        """
        self.assertFalse(False)

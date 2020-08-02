from django.contrib.auth.urls import urlpatterns
from django.db import transaction
from django.db.utils import IntegrityError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core import exceptions
from userprofile.models import Profile
from django.contrib.auth.models import User
from test_suite.common import test_data
from test_suite.common.test_methods import *

from userprofile.serializers import ProfileSerializer
import json
import copy

# iso_profile = test_data.iso_profile
TEST_PROFILES = test_data.profiles


class TestProfileCreateAndRead(APITestCase):
    """
    This tests the:
        - create(/profiles[POST]),
        - list(/profiles[GET]),
        - detail(/profile/{profile.pk_uuid}[GET]),
            - TODO:
                - Detail GET if profile is private
    endpoints

    """

    def setUp(self):
        for profile in TEST_PROFILES[:3]:  # Not inclusive
            serializer = ProfileSerializer(data=profile)
            serializer.is_valid()
            serializer.save()

    def test_create_profile(self):
        """
        Ensure we can create a new profile object.
        """
        url = reverse('profiles-list')
        profile = copy.deepcopy(TEST_PROFILES[3])
        self.assertEqual(
            Profile.objects.all().count(),
            3)

        response = self.client.post(url, profile, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = json.loads(response.content)
        self.assertEqual(
            Profile.objects.filter(pk_uuid=response_data['pk_uuid']).count(),
            1)
        self.assertEqual(
            Profile.objects.all().count(),
            4)

    def test_list_all_profiles(self):
        """
        Ensure we can create a new profile object.
        """
        url = reverse('profiles-list')
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(response.content)

        self.assertIn(TEST_PROFILES[0]['username'], [
            profile['username'] for profile in response_data])
        self.assertNotIn(TEST_PROFILES[3]['username'], [
            profile['username'] for profile in response_data])

        for profile in response_data:
            pk_uuid = profile['pk_uuid']
            self.assertEqual(Profile.objects.filter(
                pk_uuid=pk_uuid).count(), 1)

        self.assertEqual(len(response_data), 3)
        self.assertEqual(len(Profile.objects.all()), len(response_data), 3)

    def test_get_profile(self):
        """
        Ensure we can create a new profile object.
        """
        profile = get_profile(TEST_PROFILES[0]['username'])
        url = reverse('profiles-detail', args=[profile.pk_uuid])
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = json.loads(response.content)
        self.assertEqual(response_data['username'], profile.user.username)

    def test_login(self):
        login_url = reverse('login')
        username = TEST_PROFILES[0]['username']
        password = TEST_PROFILES[0]['password']
        data = {
            'username': username,
            'password': password
        }
        try:
            # Using try with transaction.atomic() instead of just with
            # prevents a bug that doesn't roll back non-consistant transactions
            # by making those transaction atomic.
            #
            # checks profile does not have a token
            with transaction.atomic():
                get_profile(username).user.auth_token.key
                self.fail('Profile by {}, has a Token'.format(username))
        except exceptions.ObjectDoesNotExist:
            self.assertTrue(True)

        response = self.client.post(login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = json.loads(response.content)
        response_profile = response_data['profile']
        response_token = response_data['token']
        current_user_token = get_profile(username).user.auth_token.key
        self.assertEqual(response_token, current_user_token)

    def test_logout(self):
        """Test Login."""
        username = TEST_PROFILES[0]['username']
        password = TEST_PROFILES[0]['password']
        try:
            # checks profile does not have a token
            with transaction.atomic():
                get_profile(username).user.auth_token.key
                self.fail('Profile by {}, has a Token'.format(username))
        except exceptions.ObjectDoesNotExist:
            self.assertTrue(True)

        response = login(self.client, username, password)
        profile_token = None
        profile_token = get_profile(username).user.auth_token.key
        self.assertIsNotNone(profile_token)

        # Set Authorization Header
        self.client.credentials(
            HTTP_AUTHORIZATION='Token {}'.format(profile_token)
        )

        logout_url = reverse('logout')
        response = self.client.post(logout_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = json.loads(response.content)
        self.assertIsNone(response_data['token'])
        self.assertIsNone(response_data['profile'])

        try:
            # checks profile does not have a token
            with transaction.atomic():
                get_profile(username).user.auth_token.key
                self.fail('Profile by {}, has a Token'.format(username))
        except exceptions.ObjectDoesNotExist:
            self.assertTrue(True)


class TestProfilePartialUpdate(APITestCase):
    def setUp(self):
        for profile in TEST_PROFILES[:3]:  # Not inclusive
            serializer = ProfileSerializer(data=profile)
            serializer.is_valid()
            serializer.save()

    def test_partial_update_profile(self):
        username = TEST_PROFILES[0]['username']
        password = TEST_PROFILES[0]['password']
        current_profile = authorize(self.client, username, password)

        detail_url = reverse(
            'profiles-detail', args=[current_profile.pk_uuid])
        self.assertEquals(current_profile.user.username, username)
        # Partial Update
        response = self.client.patch(
            detail_url, data={'bio': 'Really'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_logged_in_profile = get_profile(username)
        self.assertEqual(updated_logged_in_profile.bio, 'Really')

    def test_partial_with_repeated_value_update_profile(self):
        username = TEST_PROFILES[0]['username']
        password = TEST_PROFILES[0]['password']
        current_profile = authorize(self.client, username, password)

        detail_url = reverse(
            'profiles-detail', args=[current_profile.pk_uuid])
        # Partial Update
        response = self.client.patch(
            detail_url,
            {
                'username': TEST_PROFILES[1]['username'],
                'email': TEST_PROFILES[1]['email'],
            },
            format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = json.loads(response.content)
        self.assertIn('username', response_data.keys())

    def test_unauthorized_partial_update_profile(self):
        username = TEST_PROFILES[0]['username']
        password = TEST_PROFILES[0]['password']
        current_profile = get_profile(username)
        detail_url = reverse(
            'profiles-detail', args=[current_profile.pk_uuid])

        # Partial Update
        response = self.client.patch(
            detail_url, {'bio': 'Really'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        updated_logged_in_profile = get_profile(username)
        self.assertEqual(updated_logged_in_profile.bio, current_profile.bio)

    def test_updating_wrong_profile(self):
        username = TEST_PROFILES[0]['username']
        password = TEST_PROFILES[0]['password']
        response_data = authorize(self.client, username, password)
        current_profile = authorize(self.client, username, password)

        # Update current profile SHOULD WORK
        detail_url = reverse(
            'profiles-detail', args=[current_profile.pk_uuid])

        # Partial Update
        response = self.client.patch(
            detail_url, {'bio': 'Really'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_logged_in_profile = get_profile(current_profile.user.username)
        self.assertEqual(updated_logged_in_profile.bio, 'Really')

        # Update current profile SHOULD NOT WORK
        other_profile = get_profile(TEST_PROFILES[1]['username'])
        detail_url = reverse(
            'profiles-detail', args=[other_profile.pk_uuid])
        # Partial Update
        response = self.client.patch(
            detail_url, {'bio': 'Really'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        updated_other_profile = get_profile(other_profile.user.username)
        self.assertEqual(other_profile.bio, updated_other_profile.bio)


class TestProfileFullUpdate(APITestCase):
    def setUp(self):
        for profile in TEST_PROFILES[:3]:  # Not inclusive
            serializer = ProfileSerializer(data=profile)
            serializer.is_valid()
            serializer.save()

    def test_full_update_profile(self):
        """
        Ensure we can change the data in a profile.
        """

        username = TEST_PROFILES[0]['username']
        password = TEST_PROFILES[0]['password']
        current_profile = authorize(self.client, username, password)
        detail_url = reverse(
            'profiles-detail', args=[current_profile.pk_uuid])

        profile_to_update = TEST_PROFILES[0]
        profile_to_update['bio'] = 'I\'ve been updated'

        # Full update
        response = self.client.put(
            detail_url, profile_to_update, format='json')
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_profile = get_profile(profile_to_update['username'])

        self.assertEqual(current_profile.pk_uuid, updated_profile.pk_uuid)
        self.assertEqual(updated_profile.bio, profile_to_update['bio'])

    def test_full_with_repeated_unique_value_update_profile(self):
        username = TEST_PROFILES[0]['username']
        password = TEST_PROFILES[0]['password']
        current_profile = authorize(self.client, username, password)

        detail_url = reverse(
            'profiles-detail', args=[current_profile.pk_uuid])
        # Partial Update
        profile_to_update = copy.deepcopy(TEST_PROFILES[0])
        profile_to_update['username'] = TEST_PROFILES[1]['username']

        response = self.client.put(
            detail_url, profile_to_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = json.loads(response.content)
        self.assertIn('username', response_data.keys())

    def test_unauthorized_full_update_profile(self):
        username = TEST_PROFILES[0]['username']
        password = TEST_PROFILES[0]['password']
        current_profile = get_profile(username)
        detail_url = reverse(
            'profiles-detail', args=[current_profile.pk_uuid])

        # Partial Update
        profile_to_update = copy.deepcopy(TEST_PROFILES[0])
        profile_to_update['username'] = TEST_PROFILES[1]['username']

        response = self.client.put(
            detail_url, profile_to_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        updated_logged_in_profile = get_profile(username)
        self.assertEqual(updated_logged_in_profile.bio, current_profile.bio)

    def test_updating_wrong_profile(self):
        username = TEST_PROFILES[0]['username']
        password = TEST_PROFILES[0]['password']
        current_profile = authorize(self.client, username, password)

        # Update current profile SHOULD WORK
        detail_url = reverse(
            'profiles-detail', args=[current_profile.pk_uuid])

        # Partial Update
        profile_to_update = copy.deepcopy(TEST_PROFILES[0])
        profile_to_update['bio'] = 'I should work'
        response = self.client.put(
            detail_url, profile_to_update, format='json')
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_profile = get_profile(profile_to_update['username'])

        self.assertEqual(current_profile.pk_uuid, updated_profile.pk_uuid)
        self.assertEqual(updated_profile.bio, profile_to_update['bio'])

        # Update current profile SHOULD NOT WORK

        profile_to_update = copy.deepcopy(TEST_PROFILES[1])
        profile_to_update['bio'] = 'I should not work'
        other_profile = get_profile(profile_to_update['username'])
        detail_url = reverse(
            'profiles-detail', args=[other_profile.pk_uuid])

        response = self.client.put(
            detail_url, profile_to_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestProfileDelete(APITestCase):
    def setUp(self):
        for profile in TEST_PROFILES[:3]:  # Not inclusive
            serializer = ProfileSerializer(data=profile)
            serializer.is_valid()
            serializer.save()

    def test_unauthorized_delete_profile(self):
        """
        Ensure we can destroy a profile object.
        """

        profile = get_profile('user1')
        self.assertEqual(profile.user.username, 'user1')

        url = reverse('profiles-detail', args=[profile.pk_uuid])
        response = self.client.delete(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Check changed object still exists
        try:
            with transaction.atomic():
                self.assertEqual(profile, get_profile('user1'))
        except exceptions.ObjectDoesNotExist:
            self.fail('Unauthorized delete permitted')

    def test_authorized_delete_profile(self):
        """
        Ensure we can destroy a profile object.
        """
        username = TEST_PROFILES[0]['username']
        password = TEST_PROFILES[0]['password']
        profile = authorize(self.client, username, password)
        self.assertEqual(profile.user.username, username)

        url = reverse('profiles-detail', args=[profile.pk_uuid])
        response = self.client.delete(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check changed object does not exists
        try:
            with transaction.atomic():
                self.assertEqual(profile, get_profile(username))
                self.fail('Profile with username {} should have been deleted'
                          .format(username)
                          )
        except exceptions.ObjectDoesNotExist:
            self.assertTrue(True)

        # Get deleted profile should return 404
        url = reverse('profiles-detail', args=[profile.pk_uuid])
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Delete deleted profile should return 404
        url = reverse('profiles-detail', args=[profile.pk_uuid])
        response = self.client.delete(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_incorrect_profile(self):
        username = TEST_PROFILES[0]['username']
        password = TEST_PROFILES[0]['password']
        profile = authorize(self.client, username, password)
        self.assertEqual(profile.user.username, username)

        profile_to_delete = get_profile(TEST_PROFILES[1]['username'])

        url = reverse('profiles-detail', args=[profile_to_delete.pk_uuid])
        response = self.client.delete(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Get deleted profile should return 200
        url = reverse('profiles-detail', args=[profile.pk_uuid])
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestProfileFollow(APITestCase):
    def setUp(self):
        for profile in TEST_PROFILES:  # Not inclusive
            serializer = ProfileSerializer(data=profile)
            serializer.is_valid(raise_exception=True)
            serializer.save()

    def test_follow_profile_thar_does_not_exist(self):
        profile_following_username = TEST_PROFILES[0]['username']
        profile_following_password = TEST_PROFILES[0]['password']
        profile_following = authorize(
            self.client,
            profile_following_username,
            profile_following_password
        )

        # Follow
        follow_url = reverse(
            'profiles-follow', args=['00000000-0000-0000-0000-000000000000'])
        response = self.client.post(follow_url, None, format='json')

        # Expect follow
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(0, profile_following.following.all().count())

    def test_follow_private_profile(self):
        profile_following_username = TEST_PROFILES[0]['username']
        profile_following_password = TEST_PROFILES[0]['password']
        profile_following = authorize(
            self.client,
            profile_following_username,
            profile_following_password
        )
        profile_to_follow_username = TEST_PROFILES[5]['username']
        profile_to_follow_password = TEST_PROFILES[5]['password']
        profile_to_follow = get_profile(profile_to_follow_username)

        self.assertTrue(profile_to_follow.is_private)
        follow_url = reverse(
            'profiles-follow', args=[profile_to_follow.pk_uuid])
        response = self.client.post(follow_url, None, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(profile_to_follow, profile_following.following.all())

        # TODO: Add Follow Request test

    def test_unauthorized_follow(self):
        profile_following_username = TEST_PROFILES[0]['username']
        profile_following_password = TEST_PROFILES[0]['password']
        profile_following = get_profile(profile_following_username)

        profile_to_follow_username = TEST_PROFILES[0]['username']
        profile_to_follow_password = TEST_PROFILES[0]['password']
        profile_to_follow = get_profile(profile_to_follow_username)

        # Follow
        follow_url = reverse(
            'profiles-follow', args=[profile_to_follow.pk_uuid])
        response = self.client.post(follow_url, None, format='json')

        # Expect follow
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(0, profile_following.following.all().count())

    def test_follow_self(self):
        profile_following_username = TEST_PROFILES[0]['username']
        profile_following_password = TEST_PROFILES[0]['password']
        profile_following = authorize(
            self.client,
            profile_following_username,
            profile_following_password
        )
        profile_to_follow_username = TEST_PROFILES[0]['username']
        profile_to_follow_password = TEST_PROFILES[0]['password']
        profile_to_follow = get_profile(profile_to_follow_username)

        # Follow
        follow_url = reverse(
            'profiles-follow', args=[profile_to_follow.pk_uuid])
        response = self.client.post(follow_url, None, format='json')

        # Expect follow
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotIn(profile_to_follow, profile_following.following.all())
        self.assertNotIn(profile_following, profile_to_follow.following.all())

    def test_follow(self):
        profile_following_username = TEST_PROFILES[0]['username']
        profile_following_password = TEST_PROFILES[0]['password']
        profile_following = authorize(
            self.client,
            profile_following_username,
            profile_following_password
        )
        profile_to_follow_username = TEST_PROFILES[1]['username']
        profile_to_follow_password = TEST_PROFILES[1]['password']
        profile_to_follow = get_profile(profile_to_follow_username)

        # Follow
        follow_url = reverse(
            'profiles-follow', args=[profile_to_follow.pk_uuid])
        response = self.client.post(follow_url, None, format='json')

        # Expect follow
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(profile_to_follow, profile_following.following.all())
        self.assertNotIn(profile_following, profile_to_follow.following.all())

    # def test_follow_request_on_private_profile(self):
    #     profile_1 = get_profile('user1')
    #     profile_2 = get_profile('user2')

    #     # Login User2
    #     login(self, profiles[1]['username'], profiles[1]['password'])
    #     set_auth_header(self, 'user2')

    #     # Follow User1
    #     follow_url = reverse('profiles-follow', args=[profile_1.id])
    #     response = self.client.post(follow_url, None, format='json')

    #     # Expect placed in request list
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIn(profile_2, profile_1.follow_requests_received.all())
    #     self.assertNotIn(profile_1, profile_2.following.all())

    # def test_accept_follow_request(self):
    #     profile_1 = get_profile('user1')
    #     profile_2 = get_profile('user2')

    #     # Login User2
    #     login(self, profiles[1]['username'], profiles[1]['password'])
    #     set_auth_header(self, 'user2')

    #     # User2 follow user1
    #     follow_url = reverse('profiles-follow', args=[profile_1.id])
    #     response = self.client.post(follow_url, None, format='json')

    #     # Login User1
    #     login(self, profiles[0]['username'], profiles[0]['password'])
    #     set_auth_header(self, 'user1')

    #     # Accept Follow request
    #     accept_request = reverse(
    #         'profiles-accept-follow-request', args=[profile_2.id])
    #     response = self.client.post(accept_request, None, format='json')

    #     # Expect now Following
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIn(profile_1, profile_2.following.all())

    # def test_reject_follow_request(self):
    #     profile_1 = get_profile('user1')
    #     profile_2 = get_profile('user2')

    #     # Login User2
    #     login(self, profiles[1]['username'], profiles[1]['password'])
    #     set_auth_header(self, 'user2')

    #     # User2 follow user1
    #     follow_url = reverse('profiles-follow', args=[profile_1.id])
    #     response = self.client.post(follow_url, None, format='json')

    #     # Login User1
    #     login(self, profiles[0]['username'], profiles[0]['password'])
    #     set_auth_header(self, 'user1')

    #     # Accept Follow request
    #     accept_request = reverse(
    #         'profiles-reject-follow-request', args=[profile_2.id])
    #     response = self.client.post(accept_request, None, format='json')

    #     # Expect not Following
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertNotIn(profile_1, profile_2.following.all())

    # def test_unfollow(self):
    #     profile_1 = get_profile('user1')
    #     profile_2 = get_profile('user2')
    #     profile_3 = get_profile('user3')
    #     profile_4 = get_profile('user4')

    #     # Login User1
    #     login(self, profiles[0]['username'], profiles[0]['password'])
    #     set_auth_header(self, 'user1')

    #     # User1 follow user2
    #     follow_url = reverse('profiles-follow', args=[profile_2.id])
    #     response = self.client.post(follow_url, None, format='json')

    #     # User1 follow user3
    #     follow_url = reverse('profiles-follow', args=[profile_3.id])
    #     response = self.client.post(follow_url, None, format='json')

    #     # User1 follow user4
    #     follow_url = reverse('profiles-follow', args=[profile_4.id])
    #     response = self.client.post(follow_url, None, format='json')

    #     self.assertNotIn(profile_1, profile_2.following.all())
    #     self.assertNotIn(profile_1, profile_3.following.all())
    #     self.assertNotIn(profile_1, profile_4.following.all())

    #     # Unfollow
    #     accept_request = reverse(
    #         'profiles-unfollow', args=[profile_2.id])
    #     response = self.client.post(accept_request, None, format='json')

    #     # Expect not Following User2
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertNotIn(profile_2, profile_1.following.all())

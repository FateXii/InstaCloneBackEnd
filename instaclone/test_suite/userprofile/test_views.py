from django.contrib.auth.urls import urlpatterns
from django.db import transaction
from django.db.utils import IntegrityError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core import exceptions
from userprofile.models import Profile, FollowRequests
from django.contrib.auth.models import User
from test_suite.common import test_data
from test_suite.common.test_methods import *

from userprofile.serializers import ProfileSerializer, BaseProfileSerializer
import json
import copy

TEST_PROFILES = test_data.profiles
ZERO_UUID = '00000000-0000-0000-0000-000000000000'


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

    def test_delete_profile_that_does_not_exist(self):
        username = TEST_PROFILES[0]['username']
        password = TEST_PROFILES[0]['password']
        profile = authorize(self.client, username, password)
        self.assertEqual(profile.user.username, username)

        # Delete deleted profile should return 404
        url = reverse('profiles-detail', args=[ZERO_UUID])
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
        for profile in TEST_PROFILES:
            serializer = ProfileSerializer(data=profile)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        get_profile('user3').following.add(get_profile('user2'))
        get_profile('user3').following.add(get_profile('user1'))
        get_profile('user4').following.add(get_profile('user0'))

    def test_follow_profile_that_does_not_exist(self):
        profile_following_username = TEST_PROFILES[0]['username']
        profile_following_password = TEST_PROFILES[0]['password']
        profile_following = authorize(
            self.client,
            profile_following_username,
            profile_following_password
        )

        # Follow
        follow_url = reverse(
            'profiles-follow', args=[ZERO_UUID])
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

    def test_unfollow(self):
        current_profile = authorize(
            self.client,
            'user3',
            'pass1234'
        )
        profile_to_unfollow = get_profile('user1')

        self.assertIn(profile_to_unfollow, current_profile.following.all())
        follow_url = reverse(
            'profiles-unfollow', args=[profile_to_unfollow.pk_uuid])
        response = self.client.post(follow_url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(profile_to_unfollow, current_profile.following.all())

    def test_unfollow_wrong_profile(self):
        current_profile = authorize(
            self.client,
            'user0',
            'pass1234'
        )
        profile_to_unfollow = get_profile('user3')

        self.assertNotIn(profile_to_unfollow, current_profile.following.all())
        follow_url = reverse(
            'profiles-unfollow', args=[profile_to_unfollow.pk_uuid])
        response = self.client.post(follow_url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotIn(profile_to_unfollow, current_profile.following.all())


class TestFollowRequests(APITestCase):
    def setUp(self):
        for profile in TEST_PROFILES:
            serializer = ProfileSerializer(data=profile)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        follow_requests = [
            FollowRequests(
                request_from=get_profile('user1'),
                request_to=get_profile('user6')
            ),
            FollowRequests(
                request_from=get_profile('user1'),
                request_to=get_profile('user7')
            ),
            FollowRequests(
                request_from=get_profile('user1'),
                request_to=get_profile('user8')
            ),
            FollowRequests(
                request_from=get_profile('user1'),
                request_to=get_profile('user9')
            ),
            FollowRequests(
                request_from=get_profile('user2'),
                request_to=get_profile('user7')
            ),
            FollowRequests(
                request_from=get_profile('user7'),
                request_to=get_profile('user5')
            ),
            FollowRequests(
                request_from=get_profile('user7'),
                request_to=get_profile('user6')
            ),
            FollowRequests(
                request_from=get_profile('user7'),
                request_to=get_profile('user8')
            ),
            FollowRequests(
                request_from=get_profile('user7'),
                request_to=get_profile('user9')
            ),
        ]
        get_profile('user3').following.add(get_profile('user7'))
        for request in follow_requests:
            request.save()
        self.INITIAL_REQUEST_COUNT = len(follow_requests)

    def test_add_follow_request(self):
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
        self.assertEqual(self.INITIAL_REQUEST_COUNT,
                         FollowRequests.objects.all().count())

        follow_url = reverse(
            'profiles-follow', args=[profile_to_follow.pk_uuid])
        response = self.client.post(follow_url, None, format='json')

        self.assertEqual(self.INITIAL_REQUEST_COUNT + 1,
                         FollowRequests.objects.all().count())
        self.assertEqual(1,
                         profile_to_follow.requests_received.filter(
                             request_from=profile_following).count()
                         )

        self.assertEqual(
            profile_to_follow
            .requests_received
            .get(
                request_from=profile_following
            ).request_from, profile_following
        )

        self.assertEqual(
            profile_following
            .requests_sent
            .get(
                request_to=profile_to_follow
            ).request_to,
            profile_to_follow
        )

    def test_repeated_add_request(self):
        profile_following = authorize(
            self.client,
            'user1',
            'pass1234',
        )
        profile_to_follow = get_profile('user6')

        self.assertTrue(profile_to_follow.is_private)
        self.assertEqual(self.INITIAL_REQUEST_COUNT,
                         FollowRequests.objects.all().count())
        follow_url = reverse(
            'profiles-follow', args=[profile_to_follow.pk_uuid])
        response = self.client.post(follow_url, None, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.INITIAL_REQUEST_COUNT,
                         FollowRequests.objects.all().count())

        self.assertEqual(
            1,
            profile_following
            .requests_sent
            .filter(request_to=profile_to_follow)
            .count()
        )

    def test_list_not_authorized(self):
        working_profile = get_profile('user1')

        request_list = reverse(
            'requests-sent', args=[working_profile.pk_uuid])
        response = self.client.get(request_list, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_not_current_user(self):
        working_profile = get_profile('user1')
        current_profile = authorize(
            self.client,
            'user2',
            'pass1234'
        )
        # Not following request
        request_list = reverse(
            'requests-sent', args=[working_profile.pk_uuid])
        response = self.client.get(request_list, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_authorized_current_user(self):

        current_profile = authorize(
            self.client,
            'user7',
            'pass1234'
        )

        request_list = reverse(
            'requests-sent', args=[current_profile.pk_uuid])
        response = self.client.get(request_list, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(response.content)

        for field in ['pk_uuid',  'username', 'email',
                      'first_name', 'last_name', 'bio', 'phone_number',
                      'is_private'
                      ]:
            for response in response_data:
                self.assertIn(field, response.keys())

        self.assertEqual(
            ['user9', 'user8', 'user5', 'user6', ].sort(),
            [response['username'] for response in response_data].sort()
        )

    def test_list_requests_received(self):
        current_profile = authorize(
            self.client,
            'user6',
            'pass1234'
        )
        request_list = reverse(
            'requests-received', args=[current_profile.pk_uuid])
        response = self.client.get(request_list, {}, format='json')
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(response_data))

        for field in ['pk_uuid',  'username', 'email',
                      'first_name', 'last_name', 'bio', 'phone_number',
                      'is_private'
                      ]:
            for response in response_data:
                self.assertIn(field, response.keys())

        self.assertEqual(
            ['user1', 'user7', ]
            .sort(),
            [response['username'] for response in response_data]
            .sort()
        )

    def test_get_follow_request(self):
        current_profile = authorize(
            self.client,
            'user6',
            'pass1234'
        )
        request = current_profile.requests_received.get(
            request_from=get_profile('user1'))
        request_list = reverse(
            'requests-detail',
            args=[current_profile.pk_uuid, request.pk_uuid])
        response = self.client.get(request_list, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(response.content)
        self.assertEqual(
            str(current_profile.pk_uuid),
            response_data['request_to']['pk_uuid']
        )
        self.assertEqual(
            str(get_profile('user1').pk_uuid),
            response_data['request_from']['pk_uuid']
        )
        self.assertIsNone(response_data['accepted'])

    def test_get_follow_request_to_wrong_profile(self):
        current_profile = authorize(
            self.client,
            'user6',
            'pass1234'
        )
        request = get_profile('user7').requests_received.get(
            request_from=get_profile('user1'))
        request_list = reverse(
            'requests-detail',
            args=[current_profile.pk_uuid, request.pk_uuid])
        response = self.client.get(request_list, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_accept_follow_request(self):
        current_profile = authorize(
            self.client,
            'user6',
            'pass1234'
        )
        request = current_profile.requests_received.get(
            request_from=get_profile('user1'))
        request_list = reverse(
            'requests-accept',
            args=[current_profile.pk_uuid, request.pk_uuid]
        )
        response = self.client.post(request_list, {}, format='json')
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check accepted
        self.assertIsNotNone(current_profile.requests_received.get(
            request_from=get_profile('user1')).accepted)
        # Check Not rejected
        self.assertIsNone(current_profile.requests_received.get(
            request_from=get_profile('user1')).rejected)
        # Check following
        self.assertIn(current_profile, get_profile('user1').following.all())

    def test_accept_wrong_follow_request(self):
        current_profile = authorize(
            self.client,
            'user6',
            'pass1234'
        )
        request = get_profile('user7').requests_received.get(
            request_from=get_profile('user1'))
        request_list = reverse(
            'requests-reject',
            args=[current_profile.pk_uuid, request.pk_uuid]
        )
        response = self.client.post(request_list, {}, format='json')
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Check Not accepted
        self.assertIsNone(current_profile.requests_received.get(
            request_from=get_profile('user1')).accepted)
        # Check Not rejected
        self.assertIsNone(current_profile.requests_received.get(
            request_from=get_profile('user1')).rejected)
        # Check not following
        self.assertNotIn(current_profile, get_profile('user1').following.all())

    def test_accept_request_that_does_not_exist(self):
        current_profile = authorize(
            self.client,
            'user6',
            'pass1234'
        )
        request_list = reverse(
            'requests-accept',
            args=[current_profile.pk_uuid, ZERO_UUID]
        )
        response = self.client.post(request_list, {}, format='json')
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_reject_follow_request(self):
        current_profile = authorize(
            self.client,
            'user7',
            'pass1234'
        )
        request = current_profile.requests_received.get(
            request_from=get_profile('user1'))
        request_list = reverse(
            'requests-reject',
            args=[current_profile.pk_uuid, request.pk_uuid]
        )
        response = self.client.post(request_list, {}, format='json')
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check Not accepted
        self.assertIsNone(current_profile.requests_received.get(
            request_from=get_profile('user1')).accepted)
        # Check rejected
        self.assertIsNotNone(current_profile.requests_received.get(
            request_from=get_profile('user1')).rejected)
        # Check not following
        self.assertNotIn(current_profile, get_profile('user1').following.all())

        # profile_1 = get_profile('user1')
        # profile_2 = get_profile('user2')

        # # Login User2
        # login(self, profiles[1]['username'], profiles[1]['password'])
        # set_auth_header(self, 'user2')

        # # User2 follow user1
        # follow_url = reverse('profiles-follow', args=[profile_1.id])
        # response = self.client.post(follow_url, None, format='json')

        # # Login User1
        # login(self, profiles[0]['username'], profiles[0]['password'])
        # set_auth_header(self, 'user1')

        # # Accept Follow request
        # accept_request = reverse(
        #     'profiles-reject-follow-request', args=[profile_2.id])
        # response = self.client.post(accept_request, None, format='json')

        # # Expect not Following
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertNotIn(profile_1, profile_2.following.all())

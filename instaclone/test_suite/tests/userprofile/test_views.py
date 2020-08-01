from django.contrib.auth.urls import urlpatterns
from django.db import transaction
from django.db.utils import IntegrityError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core import exceptions
from userprofile.models import Profile
from django.contrib.auth.models import User
from test_suite.tests.common import test_data
from test_suite.tests.common.test_methods import *

from userprofile.serializers import ProfileSerializer
import json
import copy

# iso_profile = test_data.iso_profile
TEST_PROFILES = test_data.profiles


class TestProfile(APITestCase):

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
        try:
            profile_token = get_profile(username).user.auth_token.key
            self.assertIsNotNone(profile_token)
        except exceptions.ObjectDoesNotExist:
            self.fail('Profile by {},does not has a Token'.format(username))

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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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


# # Check changed existing username
# try:
#     # Using try with transaction.atomic() instead of just with
#     # prevents a bug that doesn't roll back non consistant transactions
#     # by making those transaction atomic.
#     #
#     # Duplicates should be prevented.
#     with transaction.atomic():
#         response = self.client.patch(
#             detail_url, {'bio': 'Really', 'username': 'user2'},
#             format='json')
# except IntegrityError:
#     pass

# # Check changed first name
# response = self.client.patch(
#     detail_url, {'bio': 'Really', 'first_name': 'user1'},
#     format='json')
# updated_logged_in_profile = Profile.objects.get(
#     user__username=self.logged_in_user_1['username'])
# self.assertEqual(response.status_code, status.HTTP_200_OK)
# self.assertEqual(updated_logged_in_profile.user.first_name, 'user1')

# # Check changed to unique username
# response = self.client.patch(
#     detail_url, {'bio': 'Really', 'username': 'user_name_unique'},
#     format='json')
# updated_logged_in_profile = Profile.objects.get(
#     user__username='user_name_unique')

# self.assertEqual(response.status_code, status.HTTP_200_OK)
# self.assertEqual(
#     updated_logged_in_profile.user.username, 'user_name_unique')

# class CreateProfileTest(APITestCase):
#     def test_create_profile(self):
#         """
#         Ensure we can create a new profile object.
#         """
#         url = reverse('profiles-list')
#         for profile in profiles:
#             response = self.client.post(url, profile, format='json')
#             self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#             self.assertEqual(
#                 len(Profile.objects.filter(
#                     user__username=profile['username'])), 1)
#         self.assertEqual(len(Profile.objects.all()), 7)
#         self.assertFalse(Profile.objects.get(
#             user__username='user3').is_private)

#     def test_login(self):
#         """
#         Ensure profile can login
#         """
#         url = reverse('profiles-list')
#         for profile in profiles:
#             response = self.client.post(url, profile, format='json')
#             self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#             self.assertEqual(
#                 len(Profile.objects.filter(
#                     user__username=profile['username'])), 1)
#         self.assertEqual(len(Profile.objects.all()), 7)
#         self.assertFalse(Profile.objects.get(
#             user__username='user3').is_private)

#         # Login Attempt
#         url = reverse('login')
#         for data in profiles:
#             data = {
#                 'username': data['username'],
#                 'password': data['password'],
#             }
#             response = self.client.post(url, data, format='json')
#             self.assertEqual(response.status_code, status.HTTP_200_OK)

#             response_data = json.loads(response.content)
#             self.assertTrue(response_data['logged_in'])
#             self.assertEqual(
#                 response_data['token'],
#                 Profile.objects.get(user__username=data['username'])
#                 .user.auth_token.key)

# class ProfileTest(APITestCase):

#     def setUp(self):
#         url = reverse('profiles-list')
#         for profile in profiles:
#             self.client.post(url, profile, format='json')
#         # Login users
#         url = reverse('login')
#         self.logged_in_user_1 = profiles[0]
#         self.logged_in_user_2 = profiles[1]

#         # Login user 1
#         login(self, self.logged_in_user_1['username'],
#               self.logged_in_user_1['password'])
#         self.user_1_token = get_user_token(self.logged_in_user_1['username'])

#         # Login user 2
#         login(self, self.logged_in_user_2['username'],
#               self.logged_in_user_2['password'])
#         self.user_2_token = get_user_token(self.logged_in_user_2['username'])

#     def test_logout(self):
#         """
#         Ensure profile can logout
#         """

#         # Logout
#         url = reverse('logout')
#         logged_in_profile = Profile.objects.get(
#             user__username=self.logged_in_user_1['username'])

#         self.client.credentials(
#             HTTP_AUTHORIZATION='Token {}'.format(
#                 logged_in_profile.user.auth_token.key
#             ))
#         # Logout user 1
#         response = self.client.post(url, {}, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         # Assert user 1 logged out
#         self.assertEqual(
#             User.objects.filter(auth_token__key=self.user_1_token).count(), 0)

#         # Assert user 2 NOT logged out
#         self.assertEqual(
#             User.objects.filter(auth_token__key=self.user_2_token).count(), 1)

#     def test_read_profile_list(self):
#         """
#         Ensure we can read a list of profile objects.
#         """
#         url = reverse('profiles-list')
#         response = self.client.get(url, None, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         response_data = json.loads(response.content)
#         response_data = sorted(
#             response_data, key=lambda profile: profile['username'])
#         expected_data = sorted(
#             profiles, key=lambda profile: profile['username'])

#         self.assertEqual(len(Profile.objects.all()), len(response_data))

#         for i in range(len(expected_data)):
#             response_profile = response_data[i]
#             expected_profile = expected_data[i]
#             self.assertEqual(
#                 response_profile['username'], expected_profile['username'])
#             self.assertEqual(
#                 response_profile['email'], expected_profile['email'])

#     def test_read_profile_detail(self):
#         """
#         Ensure we can read a specific object.
#         """

#         for i in range(len(profiles)):
#             url = reverse('profiles-detail', args=[i + 1])
#             response = self.client.get(url)
#             self.assertEqual(response.status_code, status.HTTP_200_OK)

#             response_data = json.loads(response.content)
#             self.assertEqual(
#                 response_data['id'], i + 1)
#             self.assertEqual(
#                 response_data['username'], profiles[i]['username'])
#             self.assertEqual(
#                 response_data['email'], profiles[i]['email'])

#     def test_partial_update_profile(self):
#         logged_in_profile = Profile.objects.get(
#             user__username=self.logged_in_user_1['username'])
#         set_auth_header(self, logged_in_profile.user.username)

#         detail_url = reverse('profiles-detail', args=[logged_in_profile.id])

#         # Partial Update
#         response = self.client.patch(
#             detail_url, {'bio': 'Really'}, format='json')
#         updated_logged_in_profile = Profile.objects.get(
#             user__username=self.logged_in_user_1['username'])
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(updated_logged_in_profile.bio, 'Really')

#         # Check changed existing username
#         try:
#             # Using try with transaction.atomic() instead of just with
#             # prevents a bug that doesn't roll back non consistant transactions
#             # by making those transaction atomic.
#             #
#             # Duplicates should be prevented.
#             with transaction.atomic():
#                 response = self.client.patch(
#                     detail_url, {'bio': 'Really', 'username': 'user2'},
#                     format='json')
#         except IntegrityError:
#             pass

#         # Check changed first name
#         response = self.client.patch(
#             detail_url, {'bio': 'Really', 'first_name': 'user1'},
#             format='json')
#         updated_logged_in_profile = Profile.objects.get(
#             user__username=self.logged_in_user_1['username'])
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(updated_logged_in_profile.user.first_name, 'user1')

#         # Check changed to unique username
#         response = self.client.patch(
#             detail_url, {'bio': 'Really', 'username': 'user_name_unique'},
#             format='json')
#         updated_logged_in_profile = Profile.objects.get(
#             user__username='user_name_unique')

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(
#             updated_logged_in_profile.user.username, 'user_name_unique')

#     def test_full_update_profile(self):
#         """
#         Ensure we can change the data in a profile.
#         """

#         logged_in_profile = Profile.objects.get(
#             user__username=self.logged_in_user_1['username'])
#         set_auth_header(self, logged_in_profile.user.username)
#         detail_url = reverse('profiles-detail', args=[logged_in_profile.id])

#         updated_user = self.logged_in_user_1
#         updated_user['bio'] = 'I\'ve been updated'

#         # Full update
#         response = self.client.put(detail_url, updated_user, format='json')
#         response_data = json.loads(response.content)
#         logged_in_profile = Profile.objects.get(
#             user__username=updated_user['username'])
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(logged_in_profile.bio, updated_user['bio'])

#     def test_full_update_with_duplicate_profile(self):

#         # Create iso_user and login
#         url = reverse('profiles-list')
#         self.client.post(url, iso_profile, format='json')
#         url = reverse('login')
#         login(self, iso_profile['username'], iso_profile['password'])
#         logged_in_profile = Profile.objects.get(
#             user__username=iso_profile['username'])
#         set_auth_header(self, logged_in_profile.user.username)

#         detail_url = reverse('profiles-detail', args=[logged_in_profile.id])
#         # Use duplicate username
#         updated_user = iso_profile
#         updated_user['username'] = 'user1'
#         # Check changed existing username
#         try:
#             # Using try with transaction.atomic() instead of just with
#             # prevents a bug that doesn't roll back non consistant transactions
#             # by making those transaction atomic.

#             with transaction.atomic():
#                 response = self.client.put(
#                     detail_url, updated_user, format='json')
#         except IntegrityError:
#             pass

#         # Use duplicate email
#         updated_user = iso_profile
#         updated_user['email'] = 'email11@email.com'
#         # Check changed existing username
#         try:
#             # Using try with transaction.atomic() instead of just with
#             # prevents a bug that doesn't roll back non consistant transactions
#             # by making those transaction atomic.

#             with transaction.atomic():
#                 response = self.client.put(
#                     detail_url, updated_user, format='json')
#         except IntegrityError:
#             pass

#         # Try change info on another profile
#         detail_url = reverse(
#             'profiles-detail',
#             args=[
#                 Profile.objects.get(
#                     user__username=self.logged_in_user_1['username'])
#                 .id
#             ])
#         response = self.client.patch(
#             detail_url, {'is_private': 'false'}, format='json')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_delete_profile(self):
#         """
#         Ensure we can destroy a profile object.
#         """
#         logged_in_profile = get_profile(self.logged_in_user_1['username'])
#         set_auth_header(self, logged_in_profile.user.username)

#         profile = Profile.objects.get(id=logged_in_profile.id)
#         self.assertEqual(profile.user.username, 'user1')

#         url = reverse('profiles-detail', args=[1])
#         response = self.client.delete(url, {}, format='json')
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

#         # Check changed object does not exist
#         with self.assertRaises(Profile.DoesNotExist):
#             Profile.objects.get(id=logged_in_profile.id)

# class FollowTest(APITestCase):
#     def setUp(self):
#         url = reverse('profiles-list')
#         for profile in profiles:
#             self.client.post(url, profile, format='json')

#     def test_follow(self):
#         profile_1 = get_profile('user1')
#         profile_2 = get_profile('user2')

#         # Login User1
#         login(self, profiles[0]['username'], profiles[0]['password'])
#         set_auth_header(self, 'user1')

#         # Follow User2
#         follow_url = reverse('profiles-follow', args=[profile_2.id])
#         response = self.client.post(follow_url, None, format='json')

#         # Expect follow
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn(profile_2, profile_1.following.all())

#     def test_follow_request_on_private_profile(self):
#         profile_1 = get_profile('user1')
#         profile_2 = get_profile('user2')

#         # Login User2
#         login(self, profiles[1]['username'], profiles[1]['password'])
#         set_auth_header(self, 'user2')

#         # Follow User1
#         follow_url = reverse('profiles-follow', args=[profile_1.id])
#         response = self.client.post(follow_url, None, format='json')

#         # Expect placed in request list
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn(profile_2, profile_1.follow_requests_received.all())
#         self.assertNotIn(profile_1, profile_2.following.all())

#     def test_accept_follow_request(self):
#         profile_1 = get_profile('user1')
#         profile_2 = get_profile('user2')

#         # Login User2
#         login(self, profiles[1]['username'], profiles[1]['password'])
#         set_auth_header(self, 'user2')

#         # User2 follow user1
#         follow_url = reverse('profiles-follow', args=[profile_1.id])
#         response = self.client.post(follow_url, None, format='json')

#         # Login User1
#         login(self, profiles[0]['username'], profiles[0]['password'])
#         set_auth_header(self, 'user1')

#         # Accept Follow request
#         accept_request = reverse(
#             'profiles-accept-follow-request', args=[profile_2.id])
#         response = self.client.post(accept_request, None, format='json')

#         # Expect now Following
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn(profile_1, profile_2.following.all())

#     def test_reject_follow_request(self):
#         profile_1 = get_profile('user1')
#         profile_2 = get_profile('user2')

#         # Login User2
#         login(self, profiles[1]['username'], profiles[1]['password'])
#         set_auth_header(self, 'user2')

#         # User2 follow user1
#         follow_url = reverse('profiles-follow', args=[profile_1.id])
#         response = self.client.post(follow_url, None, format='json')

#         # Login User1
#         login(self, profiles[0]['username'], profiles[0]['password'])
#         set_auth_header(self, 'user1')

#         # Accept Follow request
#         accept_request = reverse(
#             'profiles-reject-follow-request', args=[profile_2.id])
#         response = self.client.post(accept_request, None, format='json')

#         # Expect not Following
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertNotIn(profile_1, profile_2.following.all())

#     def test_unfollow(self):
#         profile_1 = get_profile('user1')
#         profile_2 = get_profile('user2')
#         profile_3 = get_profile('user3')
#         profile_4 = get_profile('user4')

#         # Login User1
#         login(self, profiles[0]['username'], profiles[0]['password'])
#         set_auth_header(self, 'user1')

#         # User1 follow user2
#         follow_url = reverse('profiles-follow', args=[profile_2.id])
#         response = self.client.post(follow_url, None, format='json')

#         # User1 follow user3
#         follow_url = reverse('profiles-follow', args=[profile_3.id])
#         response = self.client.post(follow_url, None, format='json')

#         # User1 follow user4
#         follow_url = reverse('profiles-follow', args=[profile_4.id])
#         response = self.client.post(follow_url, None, format='json')

#         self.assertNotIn(profile_1, profile_2.following.all())
#         self.assertNotIn(profile_1, profile_3.following.all())
#         self.assertNotIn(profile_1, profile_4.following.all())

#         # Unfollow
#         accept_request = reverse(
#             'profiles-unfollow', args=[profile_2.id])
#         response = self.client.post(accept_request, None, format='json')

#         # Expect not Following User2
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertNotIn(profile_2, profile_1.following.all())

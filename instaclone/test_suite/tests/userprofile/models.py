from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core import exceptions
from userprofile.models import Profile, FollowRequests
from django.contrib.auth.models import User
from rest_framework import serializers
from test_suite.tests.common import test_data
from test_suite.tests.common.test_methods import *
import copy

TEST_PROFILES = test_data.profiles


class TestUserProfileModels(APITestCase):
    def setUp(self):
        self.users = []
        self.profiles = copy.deepcopy(TEST_PROFILES)
        for profile in self.profiles:
            temp_user = {
                'username': profile.pop('username', None),
                'first_name': profile.pop('first_name', ''),
                'last_name': profile.pop('last_name', ''),
                'password': profile.pop('password', None),
                'email': profile.pop('email', None)
            }
            user = User.objects.create_user(
                **temp_user)
            Profile(user=user, **profile).save()
        return super().setUp()

    def test_user_created(self):
        all_users = User.objects.all()
        self.assertEqual(all_users.count(), 7)

        user_0 = User.objects.get(
            username=TEST_PROFILES[0]['username'])
        self.assertEqual(user_0.first_name, TEST_PROFILES[0]['first_name'])

    def test_profile_created(self):
        all_profiles = Profile.objects.all()
        self.assertEqual(all_profiles.count(), 7)

        profile_for_user_1 = Profile.objects.get(
            user__username=TEST_PROFILES[1]['username'])
        self.assertEqual(profile_for_user_1.user.first_name,
                         TEST_PROFILES[1]['first_name'])

        self.assertIsNotNone(profile_for_user_1.pk_uuid)

    def test_add_follow(self):
        profile = Profile.objects.get(
            user__username=TEST_PROFILES[1]['username'])

        profile_to_follow = Profile.objects.get(
            user__username=TEST_PROFILES[0]['username'])

        profile.following.add(profile_to_follow)
        isFollowing = bool(profile.following.all().count())
        self.assertTrue(isFollowing)
        self.assertEqual(profile_to_follow,
                         profile.following.get(
                             pk_uuid=profile_to_follow.pk_uuid)
                         )

    def test_add_follow_request(self):
        profile = Profile.objects.get(
            user__username=TEST_PROFILES[1]['username'])

        profile_to_follow = Profile.objects.get(
            user__username=TEST_PROFILES[0]['username'])

        FollowRequests(request_by=profile,
                       request_to_follow=profile_to_follow).save()

        self.assertEqual(FollowRequests.objects.all().count(), 1)

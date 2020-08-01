from rest_framework.test import APITestCase
from django.core import exceptions
from userprofile.models import Profile, FollowRequests
from userprofile.serializers import ProfileSerializer
from django.contrib.auth.models import User
from rest_framework import serializers
from test_suite.tests.common import test_data
from test_suite.tests.common.test_methods import *
import json
import copy

TEST_PROFILES = test_data.profiles


class TestProfileSerializer(APITestCase):
    def setUp(self):
        self.serializer_for_profile_0 = ProfileSerializer(
            data=TEST_PROFILES[0])
        self.serializer_for_profile_1 = ProfileSerializer(
            data=TEST_PROFILES[1])
        self.serializer_for_profile_2 = ProfileSerializer(
            data=TEST_PROFILES[2])
        self.profile_list_serializer = ProfileSerializer(
            data=TEST_PROFILES[3:],
            many=True
        )

        self.users = []
        self.profiles = copy.deepcopy(TEST_PROFILES[5:])
        self.created_profiles = []
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
            self.created_profiles.append(Profile(user=user, **profile).save())

        return super().setUp()

    def test_serializer_validator(self):
        self.assertTrue(
            self.serializer_for_profile_0.is_valid(raise_exception=True))
        self.assertTrue(
            self.serializer_for_profile_1.is_valid(raise_exception=True))
        self.assertTrue(
            self.serializer_for_profile_2.is_valid(raise_exception=True))
        self.serializer_for_profile_1.save()
        self.serializer_for_profile_0.save()
        # print(self.serializer_for_profile_1.data)
        self.assertNotIn(
            'user', self.serializer_for_profile_1.data.keys()
        )
        self.assertNotIn(
            'password', self.serializer_for_profile_0.data.keys()
        )
        self.assertNotIn(
            'password', self.serializer_for_profile_1.data.keys()
        )

    def test_serializer_get(self):
        profile = get_profile(TEST_PROFILES[5]['username'])
        serialized_profile_0 = ProfileSerializer(
            profile)

        self.assertEqual(
            serialized_profile_0.data['username'], profile.user.username)

        self.assertNotIn(
            'password', serialized_profile_0.data.keys()
        )

    def test_serializer_create(self):
        profile = ProfileSerializer(data=TEST_PROFILES[3])
        self.assertTrue(profile.is_valid(raise_exception=True))
        profile.save()

        saved_profile = get_profile(TEST_PROFILES[5]['username'])
        serialized_profile_4 = ProfileSerializer(
            saved_profile)
        self.assertEqual(
            serialized_profile_4.data['username'], saved_profile.user.username)

    def test_serializer_update(self):
        profile = get_profile(TEST_PROFILES[5]['username'])
        updated_profile = ProfileSerializer(
            instance=profile, data={
                'username': 'munique',
                'bio': 'I`ve been updated'
            }, partial=True)
        self.assertTrue(updated_profile.is_valid(raise_exception=True))
        updated_profile.save()

        updated_profile = Profile.objects.get(user__username='munique')
        self.assertEqual(updated_profile.bio, 'I`ve been updated')

    def test_unique_serializer_update(self):
        profile = get_profile(TEST_PROFILES[5]['username'])
        updated_profile = ProfileSerializer(
            instance=profile, data={
                'username': TEST_PROFILES[6]['username'],
                'bio': 'I`ve been updated'
            }, partial=True)
        self.assertFalse(updated_profile.is_valid())

        with self.assertRaises(serializers.ValidationError) as error:
            updated_profile.is_valid(raise_exception=True)

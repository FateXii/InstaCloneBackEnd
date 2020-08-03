from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core import exceptions
from userprofile.models import Profile
from django.contrib.auth.models import User
from rest_framework import serializers
from test_suite.tests.common import test_data
from test_suite.tests.common.test_methods import *

TEST_PROFILES = test_data.profiles


class TestUserProfileModels(APITestCase):
    def setUp(self):

        return super().setUp()

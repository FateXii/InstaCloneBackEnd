import copy

from django.contrib.auth.models import User
from django.core import exceptions
from django.urls import reverse
from rest_framework import serializers, status
from rest_framework.test import APITestCase

from test_suite.common import test_data
from test_suite.common.test_methods import *
from userprofile.models import Profile
from userprofile.serializers import ProfileSerializer
from posts.models import Post

TEST_PROFILES = test_data.profiles
TEST_POSTS = test_data.posts


class TestPostModel(APITestCase):
    def setUp(self):
        for profile in TEST_PROFILES:
            serializer = ProfileSerializer(data=profile)
            serializer.is_valid()
            serializer.save()

    def test_create_post_model(self):
        profile = get_profile('user0')
        Post(profile=profile, **TEST_POSTS[0]).save()
        self.assertEqual(Post.objects.all().count(), 1)
        post = Post.objects.all()[0]
        self.assertEqual(profile.posts.all()[0], post)
        self.assertEqual(
            post
            .profile
            .user
            .username, 'user0')
        self.assertEqual(post.caption, 'Jennifer Love Hewitt')

    def test_delete_model(self):
        profile = get_profile('user0')
        Post(profile=profile, **TEST_POSTS[0]).save()
        self.assertEqual(Post.objects.all().count(), 1)
        post = Post.objects.all()[0]
        Post.objects.get(profile=profile).delete()
        self.assertEqual(Post.objects.all().count(), 0)

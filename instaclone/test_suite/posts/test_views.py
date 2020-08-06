import json

from django.contrib.auth.urls import urlpatterns
from django.core import exceptions
from django.db import transaction
from django.db.utils import IntegrityError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from posts.models import Post
from test_suite.common import test_data
from test_suite.common.test_methods import *
from userprofile.models import Profile

# PROFILES = test_data.profiles
# POSTS = test_data.posts


# def login_and_set_token(testCase, username, password):
#     login(testCase, username, password)
#     set_auth_header(testCase, username)


# class PostTest(APITestCase):
#     def setUp(self):
#         create_profile_url = reverse('profiles-list')
#         self.client.post(create_profile_url, PROFILES[0], format='json')
#         self.client.post(create_profile_url, PROFILES[1], format='json')
#         self.client.post(create_profile_url, PROFILES[2], format='json')
#         self.profile_1 = get_profile(PROFILES[0]['username'])
#         self.profile_2 = get_profile(PROFILES[1]['username'])
#         self.profile_3 = get_profile(PROFILES[2]['username'])
#         return super().setUp()

#     def test_create_post(self):
#         post_creation = reverse('posts-list')
#         profile = get_profile(PROFILES[0]['username'])
#         login_and_set_token(
#             self,
#             PROFILES[0]['username'],
#             PROFILES[0]['password']
#         )

#         response = self.client.post(post_creation, POSTS[0], 'json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#         response_data = json.loads(response.content)
#         self.assertEqual(response_data['image'], POSTS[0]['image'])

#         posts = Post.objects.all()
#         self.assertEqual(posts.count(), 1)
#         self.assertEqual(posts[0].profile, profile)

#     def test_delete_post(self):
#         post_creation = reverse('posts-list')
#         # Login user 1
#         profile = get_profile(PROFILES[0]['username'])
#         login_and_set_token(
#             self,
#             PROFILES[0]['username'],
#             PROFILES[0]['password']
#         )

#         # Create 2 posts
#         self.client.post(post_creation, POSTS[0], 'json')
#         self.client.post(post_creation, POSTS[1], 'json')

#         # Delete Post 1
#         post_delete = reverse('posts-detail', args=['1'])
#         response = self.client.delete(post_delete, None, 'json')
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         posts = Post.objects.all()
#         self.assertEqual(posts.count(), 1)

#         # Login user 2
#         profile2 = get_profile(PROFILES[1]['username'])
#         self.client.credentials()
#         login_and_set_token(
#             self,
#             PROFILES[1]['username'],
#             PROFILES[1]['password']
#         )

#         # Delete post 2
#         post_delete = reverse('posts-detail', args=['2'])
#         response = self.client.delete(post_delete, None, 'json')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

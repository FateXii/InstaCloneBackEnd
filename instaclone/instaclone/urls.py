from django.contrib import admin
from django.urls import re_path, include, path
from rest_framework.authtoken import views as auth_views
from instaclone import views

urlpatterns = [
    re_path(r'', include('userprofile.urls')),
    path(r'api/login/', auth_views.obtain_auth_token, name='login'),
    path(r'api/logout/', views.logout, name='logout'),
]

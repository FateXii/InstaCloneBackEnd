from django.contrib import admin
from django.urls import re_path, include

urlpatterns = [

    re_path(r'', include('comments.urls')),
    re_path(r'', include('userprofile.urls')),
    re_path(r'', include('posts.urls')),
]

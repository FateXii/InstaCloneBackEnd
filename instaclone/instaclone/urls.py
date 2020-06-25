from django.contrib import admin
from django.urls import re_path, include


urlpatterns = [
    re_path(r'', include('userprofile.urls')),
    path(r'api/login/', views.obtain_auth_token, name='login')
]

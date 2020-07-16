from django.contrib import admin
from django.urls import re_path, include, path
from rest_framework.authtoken import views as auth_views
from . import views


urlpatterns = [
    re_path('api/', include('userprofile.urls')),
    re_path('api/', include('posts.urls')),
    # path(r'api/login/', auth_views.obtain_auth_token, name='login'),
    path(r'api/login/', views.login, name='login'),
    path(r'api/logout/', views.logout, name='logout'),
    path('admin/', admin.site.urls),
]
